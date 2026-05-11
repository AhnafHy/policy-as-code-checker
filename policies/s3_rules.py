def check_s3_policies(resources):
    findings = []
    
    for name, config in resources.items():
        if config.get('type') != 'aws_s3_bucket':
            continue
        
        attrs = config.get('attributes', {})
        
        # Check for public ACL
        acl = attrs.get('acl', '')
        if acl in ['public-read', 'public-read-write', 'authenticated-read']:
            findings.append({
                'rule_id': 'S3-001',
                'rule_name': 'S3 Bucket Public ACL',
                'severity': 'CRITICAL',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_s3_bucket',
                'message': f'S3 bucket has public ACL: {acl}',
                'remediation': 'Remove public ACL or set acl = "private"'
            })
        
        # Check for versioning
        versioning = attrs.get('versioning', {})
        if not versioning.get('enabled', False):
            findings.append({
                'rule_id': 'S3-002',
                'rule_name': 'S3 Bucket Versioning Disabled',
                'severity': 'MEDIUM',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_s3_bucket',
                'message': 'S3 bucket does not have versioning enabled',
                'remediation': 'Enable versioning: versioning { enabled = true }'
            })
        
        # Check for force_destroy in production
        if attrs.get('force_destroy', False):
            findings.append({
                'rule_id': 'S3-003',
                'rule_name': 'S3 Bucket Force Destroy Enabled',
                'severity': 'HIGH',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_s3_bucket',
                'message': 'force_destroy = true allows bucket deletion with contents',
                'remediation': 'Set force_destroy = false in production environments'
            })
        else:
            findings.append({
                'rule_id': 'S3-003',
                'rule_name': 'S3 Bucket Force Destroy Enabled',
                'severity': 'HIGH',
                'status': 'PASS',
                'resource': name,
                'resource_type': 'aws_s3_bucket',
                'message': 'force_destroy is disabled',
                'remediation': None
            })
    
    return findings