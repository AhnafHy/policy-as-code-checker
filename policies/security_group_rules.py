def check_security_group_policies(resources):
    findings = []
    
    for name, config in resources.items():
        if config.get('type') != 'aws_security_group':
            continue
        
        attrs = config.get('attributes', {})
        ingress_rules = attrs.get('ingress', [])
        
        for rule in ingress_rules:
            cidr_blocks = rule.get('cidr_blocks', [])
            from_port = rule.get('from_port', 0)
            to_port = rule.get('to_port', 0)
            protocol = rule.get('protocol', '')
            
            # Check for open to world
            if '0.0.0.0/0' in cidr_blocks:
                
                # SSH open to world
                if from_port <= 22 <= to_port:
                    findings.append({
                        'rule_id': 'SG-001',
                        'rule_name': 'SSH Open to World',
                        'severity': 'CRITICAL',
                        'status': 'FAIL',
                        'resource': name,
                        'resource_type': 'aws_security_group',
                        'message': 'Security group allows SSH (port 22) from 0.0.0.0/0',
                        'remediation': 'Restrict SSH access to specific IP ranges'
                    })
                
                # RDP open to world
                if from_port <= 3389 <= to_port:
                    findings.append({
                        'rule_id': 'SG-002',
                        'rule_name': 'RDP Open to World',
                        'severity': 'CRITICAL',
                        'status': 'FAIL',
                        'resource': name,
                        'resource_type': 'aws_security_group',
                        'message': 'Security group allows RDP (port 3389) from 0.0.0.0/0',
                        'remediation': 'Restrict RDP access to specific IP ranges'
                    })
                
                # All traffic open
                if protocol == '-1' or (from_port == 0 and to_port == 0):
                    findings.append({
                        'rule_id': 'SG-003',
                        'rule_name': 'All Traffic Open to World',
                        'severity': 'CRITICAL',
                        'status': 'FAIL',
                        'resource': name,
                        'resource_type': 'aws_security_group',
                        'message': 'Security group allows all traffic from 0.0.0.0/0',
                        'remediation': 'Restrict ingress rules to specific ports and IP ranges'
                    })
    
    return findings