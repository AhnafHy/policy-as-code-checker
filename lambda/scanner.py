import boto3
import json
import os
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import sys
sys.path.insert(0, '/var/task/policies')

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'pac-scans')

def parse_terraform(tf_code):
    resources = {}
    
    lines = tf_code.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for resource declaration
        resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        if resource_match:
            resource_type = resource_match.group(1)
            resource_name = resource_match.group(2)
            
            # Collect the full block by counting braces
            brace_count = 1
            block_lines = []
            i += 1
            
            while i < len(lines) and brace_count > 0:
                current = lines[i]
                brace_count += current.count('{') - current.count('}')
                if brace_count > 0:
                    block_lines.append(current)
                i += 1
            
            block_content = '\n'.join(block_lines)
            attrs = parse_attributes(block_content)
            
            resources[resource_name] = {
                'type': resource_type,
                'attributes': attrs
            }
        else:
            i += 1
    
    return resources

def parse_attributes(content):
    attrs = {}
    
    # Boolean values
    bool_pattern = r'(\w+)\s*=\s*(true|false)'
    for match in re.finditer(bool_pattern, content):
        key = match.group(1)
        value = match.group(2) == 'true'
        attrs[key] = value
    
    # String values
    str_pattern = r'(\w+)\s*=\s*"([^"]*)"'
    for match in re.finditer(str_pattern, content):
        key = match.group(1)
        value = match.group(2)
        attrs[key] = value
    
    # Port numbers
    port_pattern = r'(from_port|to_port)\s*=\s*(\d+)'
    for match in re.finditer(port_pattern, content):
        attrs[match.group(1)] = int(match.group(2))
    
    # CIDR blocks
    cidr_pattern = r'cidr_blocks\s*=\s*\[([^\]]*)\]'
    for match in re.finditer(cidr_pattern, content):
        cidrs = re.findall(r'"([^"]*)"', match.group(1))
        attrs['cidr_blocks'] = cidrs
    
    # Ingress blocks
    ingress_blocks = []
    ingress_pattern = r'ingress\s*\{([^}]*)\}'
    for match in re.finditer(ingress_pattern, content, re.DOTALL):
        ingress_attrs = parse_attributes(match.group(1))
        ingress_blocks.append(ingress_attrs)
    if ingress_blocks:
        attrs['ingress'] = ingress_blocks
    
    # Versioning block
    versioning_pattern = r'versioning\s*\{([^}]*)\}'
    versioning_match = re.search(versioning_pattern, content, re.DOTALL)
    if versioning_match:
        attrs['versioning'] = parse_attributes(versioning_match.group(1))
    
    # Tags block — improved to handle both formats
    # Format 1: tags = { ... }
    # Format 2: tags { ... }
    tags_pattern = r'tags\s*=?\s*\{([^}]*)\}'
    tag_match = re.search(tags_pattern, content, re.DOTALL)
    if tag_match:
        tags = {}
        tag_content = tag_match.group(1)
        tag_str_pattern = r'(\w+)\s*=\s*"([^"]*)"'
        for tm in re.finditer(tag_str_pattern, tag_content):
            tags[tm.group(1)] = tm.group(2)
        if tags:
            attrs['tags'] = tags
    
    return attrs

def run_all_policies(resources):
    from policies.s3_rules import check_s3_policies
    from policies.rds_rules import check_rds_policies
    from policies.security_group_rules import check_security_group_policies
    from policies.general_rules import check_general_policies
    
    all_findings = []
    all_findings.extend(check_s3_policies(resources))
    all_findings.extend(check_rds_policies(resources))
    all_findings.extend(check_security_group_policies(resources))
    all_findings.extend(check_general_policies(resources))
    
    return all_findings

def calculate_summary(findings):
    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    pass_count = sum(1 for f in findings if f['status'] == 'PASS')
    fail_count = sum(1 for f in findings if f['status'] == 'FAIL')
    
    for f in findings:
        if f['status'] == 'FAIL':
            severity = f.get('severity', 'LOW')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    total = pass_count + fail_count
    score = round((pass_count / total * 100), 1) if total > 0 else 0
    
    overall = 'PASS'
    if severity_counts['CRITICAL'] > 0:
        overall = 'CRITICAL'
    elif severity_counts['HIGH'] > 0:
        overall = 'HIGH'
    elif severity_counts['MEDIUM'] > 0:
        overall = 'MEDIUM'
    elif fail_count > 0:
        overall = 'LOW'
    
    return {
        'total_rules': total,
        'passed': pass_count,
        'failed': fail_count,
        'score': score,
        'overall_status': overall,
        'severity_breakdown': severity_counts
    }

def store_scan(table, scan_id, tf_code, resources, findings, summary, scan_name):
    scanned_at = datetime.now(timezone.utc).isoformat()
    
    # Store main scan record
    table.put_item(Item={
        'pk': f"SCAN#{scan_id}",
        'sk': 'METADATA',
        'scan_id': scan_id,
        'scan_name': scan_name,
        'scanned_at': scanned_at,
        'resources_found': len(resources),
        'total_rules': summary['total_rules'],
        'passed': summary['passed'],
        'failed': summary['failed'],
        'score': Decimal(str(summary['score'])),
        'overall_status': summary['overall_status'],
        'severity_critical': summary['severity_breakdown']['CRITICAL'],
        'severity_high': summary['severity_breakdown']['HIGH'],
        'severity_medium': summary['severity_breakdown']['MEDIUM'],
        'severity_low': summary['severity_breakdown']['LOW'],
        'tf_code': tf_code[:10000]  # Store first 10k chars
    })
    
    # Store individual findings
    with table.batch_writer() as batch:
        for i, finding in enumerate(findings):
            batch.put_item(Item={
                'pk': f"SCAN#{scan_id}",
                'sk': f"FINDING#{i:04d}#{finding['rule_id']}",
                'scan_id': scan_id,
                'rule_id': finding['rule_id'],
                'rule_name': finding['rule_name'],
                'severity': finding['severity'],
                'status': finding['status'],
                'resource': finding['resource'],
                'resource_type': finding['resource_type'],
                'message': finding['message'],
                'remediation': finding.get('remediation', ''),
                'scanned_at': scanned_at
            })
    
    return scanned_at

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    
    body = json.loads(event.get('body', '{}'))
    tf_code = body.get('terraform_code', '')
    scan_name = body.get('scan_name', 'Unnamed Scan')
    
    if not tf_code:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'terraform_code is required'})
        }
    
    scan_id = str(uuid.uuid4())[:8].upper()
    
    resources = parse_terraform(tf_code)
    findings = run_all_policies(resources)
    summary = calculate_summary(findings)
    scanned_at = store_scan(table, scan_id, tf_code, resources, findings, summary, scan_name)
    
    print(f"Scan {scan_id}: {len(resources)} resources, {summary['failed']} failures, score {summary['score']}%")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps({
            'scan_id': scan_id,
            'scan_name': scan_name,
            'scanned_at': scanned_at,
            'resources_found': len(resources),
            'summary': summary,
            'findings': findings
        }, default=str)
    }