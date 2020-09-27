ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tetration_inventory_tag_search

short_description: Allows for searching inventory attributes

version_added: '2.8'

description:
- Enables the querying of IP Subnets or Addresses for annotations and values 

options:
  root_scope_name:
    description:
    - Dictionary containing annotation key/value pairs
    type: dict
    required: true
  ip_address:
    description:
    - IP address to associate with annotations
    - IP subnet to associate with annotations
    - Requries one of C(ip_address) or C(ip_subnet)
    type: string
    required: false 
  ip_subnet:
    description:
    - IP subnet to associate with annotations
    - Requries one of C(ip_address) or C(ip_subnet)
    type: string
    required: false 

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.

requirements:
- requests 

author:
- Joe Jacobs (@joej164)
'''

EXAMPLES = '''
- name: Search for tags assigned to a host 
  tetration_inventory_tag_search:
    root_scope_name: Default
    ip_address: 172.16.1.10/32
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Search for tags assigned to a subnet 
  tetration_inventory_tag_search:
    root_scope_name: Default
    ip_subnet: 172.16.1.10/8
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  description: a dict with the found object 
  contains:
    key:
        description: The value in tetration the value field apply to
        returned: always
        sample: 10.0.0.0/8
        type: string
    updatedAt: 
        description: Epoch time of when the tag was last updated
        returned: always
        sample: 1601244407
        type: int 
    value: 
        description: Dictionary containg all assigned attributes and any assigned values to the subnet
        returned: always
        sample:
            Application: data
            Org: My org
        type: dict 
        
  returned: always
  type: complex
'''
from ipaddress import ip_address, ip_network

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_INVENTORY_TAG
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    ''' Main entry point for module execution
    '''
    # Module specific spec
    module_args = dict(
        root_scope_name=dict(type='str', required=True),
        ip_address=dict(type='str', required=False),
        ip_subnet=dict(type='str', required=False),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['ip_address', 'ip_subnet']
        ]
    )

    # These are all elements we put in our return JSON object for clarity
    result = {
        "object": None,
        "changed": False,
    }

    # Verify a valid IP address was passed in
    ip_object = ""

    if module.params['ip_address']:
        try:
            ip_object = str(ip_address(module.params['ip_address']))
        except ValueError:
            error_message = f"Invalid IPv4 or IPv6 Address entered.  Value entered: {module.params['ip_address']}"
            module.fail_json(msg=error_message)

    # Verify a valid IP subnet was passed in
    if module.params['ip_subnet']:
        try:
            ip_object = str(ip_network(module.params['ip_subnet']))
        except ValueError:
            error_message = f"Invalid IPv4 or IPv6 Address entered.  Value entered: {module.params['ip_subnet']}"
            module.fail_json(msg=error_message)

    tet_module = TetrationApiModule(module)

    route = f"{TETRATION_API_INVENTORY_TAG}/{module.params['root_scope_name']}/search"
    params = {'ip': ip_object}

    result['object'] = tet_module.run_method('GET', route, params=params)

    return module.exit_json(**result)


if __name__ == '__main__':
    main()
