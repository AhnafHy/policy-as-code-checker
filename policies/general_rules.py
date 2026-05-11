def check_general_policies(resources):
    findings = []
    
    REQUIRED_TAGS = ['Name', 'Environment']
    ALLOWED_REGIONS = ['us-east-2', 'us-west-2', 'eu-west-1']
    
    for name, config in resources.items():
        attrs = config.get('attributes', {})
        tags = attrs.get('tags', {})
        
        # Check required tags
        missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tags]
        if missing_tags:
            findings.append({
                'rule_id': 'GEN-001',
                'rule_name': 'Missing Required Tags',
                'severity': 'LOW',
                'status': 'FAIL',
                'resource': name,
                'resource_type': config.get('type', 'unknown'),
                'message': f'Resource is missing required tags: {", ".join(missing_tags)}',
                'remediation': f'Add tags: {", ".join(missing_tags)}'
            })
        else:
            findings.append({
                'rule_id': 'GEN-001',
                'rule_name': 'Missing Required Tags',
                'severity': 'LOW',
                'status': 'PASS',
                'resource': name,
                'resource_type': config.get('type', 'unknown'),
                'message': 'All required tags are present',
                'remediation': None
            })
    
    return findings