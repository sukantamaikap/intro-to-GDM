import re
"""
Create VM with a single disk.

Creates a Persistent Disk. Then creates an instance that attaches
that Persistent Disk as a data disk.
"""

_COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def deduce_name(base):
    """
    Deduce name from parameters
    """
    return re.sub(r'\W+', '-', base).lower()

def GenerateConfig(context):
    """
    Create instance with disks
    """
    vm_name = deduce_name(context.env['name'])
    resources = [
        {
            'type': 'compute.v1.instance',
            'name': vm_name,
            'properties': {
                'zone': context.properties['zone'],
                'machineType': ''.join([_COMPUTE_URL_BASE, 'projects/',
                        context.env['project'], '/zones/',
                        context.properties['zone'],
                        '/machineTypes/', context.properties['machineType']]),
                'metadata': {
                    'items': []
                },
                'disks': [
                    {
                        'deviceName': 'bootdisk' + vm_name,
                        'type': 'PERSISTENT',
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': 'boot-disk-' + vm_name,
                            'diskSizeGb': 20,
                            'sourceImage': ''.join([_COMPUTE_URL_BASE, 'projects/',
                                                    'centos-cloud/global/',
                                                    'images/family/centos-8'])
                        }
                    }
                ],
                'networkInterfaces': []
            }
        }
    ]

    for networkInterface in context.properties['networkInterfaces']:
        network_interface = {}
        network_interface['network'] = networkInterface['network']
        network_interface['subnetwork'] = networkInterface['subnetwork']

        if 'networkIP' in networkInterface:
            network_interface['networkIP'] = networkInterface['networkIP']

        if 'accessConfigs' in networkInterface:
            access_configs = []
            for accessConfig in networkInterface['accessConfigs']:
                access_config = {}
                access_config['name'] = deduce_name(accessConfig['name'])
                access_config['type'] = 'ONE_TO_ONE_NAT'

                if 'natIP' in accessConfig:
                    access_config['natIP'] = accessConfig['natIP']

                access_configs.append(access_config)

            network_interface['accessConfigs'] = access_configs

        resources[0]['properties']['networkInterfaces'].append(network_interface)

    return {'resources': resources}
