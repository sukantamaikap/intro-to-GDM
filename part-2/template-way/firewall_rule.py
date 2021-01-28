import re

"""
Creates firewall rules in a project.
"""

def deduce_firewall_name(name):

    """deduce firewall name from the supplied name"""
    return re.sub(r'\W+', '-', name).lower()


def CreateRules(context):

    """
    Take a list of Firewall Rule Properties in the context
    Build a list of Firewall rule Dicts

    Return list
    """

    Firewall_Rules = []
    """
    Loop through many defined firewalls and build a Dict to be append to the list
    """

    for rule in context.properties['rules']:
        given_name = rule['name']
        rule_name = deduce_firewall_name(given_name)
        rule_description = rule['description']

        # Start of our firewall list.

        Firewall_Rule = {
            'name': rule_name,
            'type': 'compute.v1.firewall'
        }
        rule_ipProtocol = rule['ipProtocol']
        rule_ipPorts = rule['ipPorts']
        rule_action = rule['action']
        rule_direction = rule['direction']
        rule_network = rule['network']
        rule_priority = rule['priority']

        #Build the Properties Key for this firewall rule Dict.
        properties = {}

        if 'sourceRanges' in rule:
            rule_SourceRanges = rule['sourceRanges']
            properties['sourceRanges'] = rule_SourceRanges

        properties['priority'] = rule_priority
        properties['direction'] = rule_direction
        properties['description'] = rule_description
        properties['network'] = rule_network

        if rule_action == 'allow':
            allowed = [{
                'IPProtocol': rule_ipProtocol,
                'ports': rule_ipPorts
                }]
            properties['allowed'] = allowed
        elif rule_action == 'deny':
            denied = [{
                'IPProtocol': rule_ipProtocol,
                'ports': rule_ipPorts
                }]
            properties['denied'] = denied

        Firewall_Rule['properties'] = properties

        Firewall_Rules.append(Firewall_Rule)

    return Firewall_Rules


def GenerateConfig(context):

    """
    Generate our Configuration

    Returns: Dictionary
    """

    resources = CreateRules(context)
    return {'resources': resources}
