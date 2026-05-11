import boto3
import json
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'pac-scans')
SCANNER_FUNCTION = os.environ.get('SCANNER_FUNCTION', '')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

def get_all_scans(table):
    result = table.scan(
        FilterExpression=Attr('sk').eq('METADATA')
    )
    scans = sorted(result.get('Items', []),
                   key=lambda x: x['scanned_at'], reverse=True)
    return [{
        'scan_id': s['scan_id'],
        'scan_name': s['scan_name'],
        'scanned_at': s['scanned_at'],
        'resources_found': int(s['resources_found']),
        'passed': int(s['passed']),
        'failed': int(s['failed']),
        'score': float(s['score']),
        'overall_status': s['overall_status'],
        'severity_critical': int(s.get('severity_critical', 0)),
        'severity_high': int(s.get('severity_high', 0)),
        'severity_medium': int(s.get('severity_medium', 0)),
        'severity_low': int(s.get('severity_low', 0))
    } for s in scans]

def get_scan_detail(table, scan_id):
    result = table.query(
        KeyConditionExpression=Key('pk').eq(f"SCAN#{scan_id}")
    )
    items = result.get('Items', [])
    
    metadata = next((i for i in items if i['sk'] == 'METADATA'), None)
    findings = [i for i in items if i['sk'].startswith('FINDING#')]
    
    if not metadata:
        return None
    
    return {
        'scan_id': metadata['scan_id'],
        'scan_name': metadata['scan_name'],
        'scanned_at': metadata['scanned_at'],
        'resources_found': int(metadata['resources_found']),
        'passed': int(metadata['passed']),
        'failed': int(metadata['failed']),
        'score': float(metadata['score']),
        'overall_status': metadata['overall_status'],
        'tf_code': metadata.get('tf_code', ''),
        'severity_breakdown': {
            'CRITICAL': int(metadata.get('severity_critical', 0)),
            'HIGH': int(metadata.get('severity_high', 0)),
            'MEDIUM': int(metadata.get('severity_medium', 0)),
            'LOW': int(metadata.get('severity_low', 0))
        },
        'findings': [{
            'rule_id': f['rule_id'],
            'rule_name': f['rule_name'],
            'severity': f['severity'],
            'status': f['status'],
            'resource': f['resource'],
            'resource_type': f['resource_type'],
            'message': f['message'],
            'remediation': f.get('remediation', '')
        } for f in sorted(findings, key=lambda x: x['sk'])]
    }

def get_dashboard_stats(table):
    result = table.scan(
        FilterExpression=Attr('sk').eq('METADATA')
    )
    scans = result.get('Items', [])
    
    if not scans:
        return {
            'total_scans': 0,
            'total_failures': 0,
            'avg_score': 0,
            'critical_findings': 0,
            'recent_scans': []
        }
    
    total_failures = sum(int(s.get('failed', 0)) for s in scans)
    avg_score = sum(float(s.get('score', 0)) for s in scans) / len(scans)
    critical = sum(int(s.get('severity_critical', 0)) for s in scans)
    
    recent = sorted(scans, key=lambda x: x['scanned_at'], reverse=True)[:5]
    
    return {
        'total_scans': len(scans),
        'total_failures': total_failures,
        'avg_score': round(avg_score, 1),
        'critical_findings': critical,
        'recent_scans': [{
            'scan_id': s['scan_id'],
            'scan_name': s['scan_name'],
            'scanned_at': s['scanned_at'],
            'score': float(s['score']),
            'overall_status': s['overall_status']
        } for s in recent]
    }

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return response(200, {})
    
    table = dynamodb.Table(TABLE_NAME)
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    params = event.get('queryStringParameters') or {}
    
    if method == 'GET' and path == '/health':
        return response(200, {'status': 'ok'})
    
    elif method == 'GET' and path == '/dashboard':
        return response(200, get_dashboard_stats(table))
    
    elif method == 'GET' and path == '/scans':
        return response(200, get_all_scans(table))
    
    elif method == 'GET' and '/scans/' in path:
        scan_id = path.split('/scans/')[-1]
        detail = get_scan_detail(table, scan_id)
        if not detail:
            return response(404, {'error': 'Scan not found'})
        return response(200, detail)
    
    elif method == 'POST' and path == '/scan':
        lambda_client = boto3.client('lambda')
        body = json.loads(event.get('body', '{}'))
        
        result = lambda_client.invoke(
            FunctionName=SCANNER_FUNCTION,
            InvocationType='RequestResponse',
            Payload=json.dumps({'body': json.dumps(body)})
        )
        
        payload = json.loads(result['Payload'].read())
        return response(
            payload.get('statusCode', 200),
            json.loads(payload.get('body', '{}'))
        )
    
    return response(404, {'error': 'Endpoint not found'})