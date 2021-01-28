import re

"""
Creates a network and its subnetworks in a project.
"""
def deduce_network_name(base):
    """
    Give a more meaningful network name & convert the string to valid resource name format
    """
    return re.sub(r'\W+', '-', base).lower()


def deduce_subnet_name(base, region, subnet_cidr):
    """
    Deduce subnet name from parameters & convert the string to valid resource name format
    """
    base = re.sub(r'\W+', '-', base).lower()
    subnet_cidr = re.sub(r'\W+', '-', subnet_cidr)
    effective_subnet_name = base + "-subnet-" + region + "-" + subnet_cidr
    return effective_subnet_name.lower()


def GenerateConfig(context):
    """
    Generates config is the entry point. GDM calls this method to consturct the payload per template.
    You must have this method present in each template file.

    GDM takse care of converting the accompanying config file into a context object per resource. context.env
    is a dictionary which contains all the params you mention above the resources section per resource.
    And context.properties is one more dictionary which contains all the properties mentioned under the resources section.
    """

    given_name = context.env['name']
    effective_vpc_name = deduce_network_name(given_name)
    # for output
    network_self_link = '$(ref.%s.selfLink)' % effective_vpc_name


    resources = [{
        'name': effective_vpc_name,
        'type': 'compute.v1.network',
        'properties': {
            'name': effective_vpc_name,
            'autoCreateSubnetworks': False,
        }
    }]

    # for output
    subnets_self_link = []

    # You can have one or more subnets associated with a network
    for subnetwork in context.properties['subnetworks']:
        subnet_name = deduce_subnet_name(given_name, subnetwork['region'], subnetwork['cidr'])
        subnet = {
            'name': subnet_name,
            'type': 'compute.v1.subnetwork',
            'properties': {
                'name': subnet_name,
                'description': 'Subnetwork of %s in %s created by GDM' % (effective_vpc_name, subnetwork['region']),
                'ipCidrRange': subnetwork['cidr'],
                'region': subnetwork['region'],
                'network': '$(ref.%s.selfLink)' % effective_vpc_name,
            },
            'metadata': {
                'dependsOn': [
                    effective_vpc_name,
                ]
            }
        }

        resources.append(subnet)
        subnets_self_link.append('$(ref.%s.selfLink)' % subnet_name)

    # Expects the return object to be a dictionary of directories with keys resources and outputs
    # and value for be anothe dictionary containing the final payload
    return {
        'resources': resources,
        'outputs': [
            {
                'name': 'network',
                'value': network_self_link
            },
            {
                'name': 'subnetworks',
                'value': subnets_self_link
            }
        ]
    }
