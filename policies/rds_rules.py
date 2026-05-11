def check_rds_policies(resources):
    findings = []
    
    for name, config in resources.items():
        if config.get('type') != 'aws_db_instance':
            continue
        
        attrs = config.get('attributes', {})
        
        # Check encryption
        if not attrs.get('storage_encrypted', False):
            findings.append({
                'rule_id': 'RDS-001',
                'rule_name': 'RDS Encryption at Rest Disabled',
                'severity': 'HIGH',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_db_instance',
                'message': 'RDS instance does not have storage encryption enabled',
                'remediation': 'Set storage_encrypted = true'
            })
        else:
            findings.append({
                'rule_id': 'RDS-001',
                'rule_name': 'RDS Encryption at Rest Disabled',
                'severity': 'HIGH',
                'status': 'PASS',
                'resource': name,
                'resource_type': 'aws_db_instance',
                'message': 'RDS storage encryption is enabled',
                'remediation': None
            })
        
        # Check Multi-AZ
        if not attrs.get('multi_az', False):
            findings.append({
                'rule_id': 'RDS-002',
                'rule_name': 'RDS Multi-AZ Disabled',
                'severity': 'MEDIUM',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_db_instance',
                'message': 'RDS instance is not configured for Multi-AZ deployment',
                'remediation': 'Set multi_az = true for production databases'
            })
        
        # Check public accessibility
        if attrs.get('publicly_accessible', False):
            findings.append({
                'rule_id': 'RDS-003',
                'rule_name': 'RDS Publicly Accessible',
                'severity': 'CRITICAL',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_db_instance',
                'message': 'RDS instance is publicly accessible from the internet',
                'remediation': 'Set publicly_accessible = false'
            })
        
        # Check deletion protection
        if not attrs.get('deletion_protection', False):
            findings.append({
                'rule_id': 'RDS-004',
                'rule_name': 'RDS Deletion Protection Disabled',
                'severity': 'MEDIUM',
                'status': 'FAIL',
                'resource': name,
                'resource_type': 'aws_db_instance',
                'message': 'RDS instance does not have deletion protection enabled',
                'remediation': 'Set deletion_protection = true'
            })
    
    return findings