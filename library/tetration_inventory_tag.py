ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tetration_user_annotations

short_description: Allows for modification and deletion of query annotation

version_added: '2.9'

description:
- Enables management of Cisco Tetration user annotations.
- Enables creation, modification, deletion, and query of annotations.

options:
  attributes:
    description:
    - Dictionary containing annotation key/value pairs
    - Required if I(state=present)
    type: dict
  ip_address:
    description:
    - IP address to associate with annotations
    required: true
    type: string
  ip_subnet:
    description:
    - IP subnet to associate with annotations
    required: true
    type: string
  root_scope_name:
    description: Name of the root scope
    required: true
    type: string
  state:
    choices: [present, absent, query]
    default: present
    description: Add, change, delete columns from Tetration user annotations
    required: true
    type: string


extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.

requirements:
- requests
- 'Required API Permission(s): user_data_upload'

author:
- Brandon Beck (@techbeck03)
- Joe Jacobs (@joej164)
'''

EXAMPLES = '''
- name: Assign or update annotations to a single host
  tetration_user_annotations:
    root_scopt_name: Default
    ip_address: 172.16.1.10
    attributes:
      location: us-dc-01
      lifecycle: dev
      owner: user@company.com
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Remove attributes without deleting all attributes
  tetration_user_annotations:
    root_scopt_name: Default
    ip_address: 172.16.1.10
    attributes:
      location:
      lifecycle:
      owner:
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Assign annotations to a subnet
  tetration_user_annotations:
    root_scope_name: Default
    ip_subnet: 172.16.1.0/24
    attributes:
      location: us-dc-01
      lifecycle: dev
      owner: user@company.com
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Remove all annotations from a host
  tetration_user_annotations:
    root_scope_name: Default
    ip_address: 172.16.1.10
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Get annotations for target IP/subnet
  tetration_user_annotations:
    root_scope_name: Default
    ip_address: 172.16.1.10
    state: query
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  description: a dict with key value pairs for each annotation associated with C(ip)
    when C(state) is present or query
  returned: always
  type: complex
tet_warnings:
  description: a dict containing warnings encountered while setting annotations.
  returned: always
  type: dict
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
        attributes=dict(type='dict'),
        ip_address=dict(type='str', required=False),
        ip_subnet=dict(type='str', required=False),
        root_scope_name=dict(type='str', required=True),
        state=dict(type="str", required=True, choices=['absent', 'present', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['ip_address', 'ip_subnet']
        ],
        mutually_exclusive=[
            ['ip_address', 'ip_subnet']
        ],
        required_if=[
            ['state', 'present', ['attributes']]
        ]
    )

    ip_object = ''

    # Verify a valid IP address was passed in
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
            error_message = f"Invalid IPv4 or IPv6 subnet entered.  Value entered: {module.params['ip_subnet']}"
            module.fail_json(msg=error_message)

    # Throw error if state is absent and annotations passed
    if module.params['state'] == 'absent' and module.params['attributes'] is not None:
        module.fail_json(msg='attributes cannot be passed for state `absent` because all attributes are cleared')

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        "object": None,
        "changed": False,
        "tet_warnings": None
    }
    route = f"{TETRATION_API_INVENTORY_TAG}/{module.params['root_scope_name']}"

    # =========================================================================
    # Get current state of the object
    params = {
        'ip': ip_object
    }
    query_result = tet_module.run_method('GET', route, params=params)
    current_attributes = query_result if query_result else {}

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':
        if not tet_module.is_subset(module.params['attributes'], current_attributes):
            req_payload = {
                'ip': ip_object,
                'attributes': module.params['attributes']
            }

            result['tet_warnings'] = tet_module.run_method('POST', route, req_payload=req_payload)
            result['object'] = tet_module.run_method('GET', route, params=params)
            result['changed'] = True

        else:
            result['object'] = current_attributes

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif module.params['state'] == 'absent':
        if current_attributes:
            req_payload = {
                'ip': ip_object
            }
            tet_module.run_method('DELETE', route, req_payload=req_payload)

            result['changed'] = True

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    elif module.params['state'] == 'query':
        if current_attributes:
            result['object'] = current_attributes

    module.exit_json(**result)


if __name__ == '__main__':
    main()
