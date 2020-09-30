ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tetration_inventory_tag_headers

short_description: Allows for deleting and querying inventory tag headers

version_added: '2.9'

description:
- Allows for querying all inventory tag headers 
- Allows for deleting an inventory tag headers

notes:
- Requires the requests Python module.
- Cannot add a column header as the API does not support it.  To add a header, add a tag to a subnet

options:
  attribute:
    description:
    - String containing attribute value to delete 
    - Required if I(state=absent)
    type: string
  root_scope_name:
    description: Name of root scope of the organization
    required: true
    type: string
  state:
    choices: [absent, query]
    description: Query the current attributes or mark an attribute as should be absent from the system 
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

requirements:
- requests 

author: 
- Joe Jacobs(@joej164)
'''

EXAMPLES = '''
- name: List all attributes in the system 
  tetration_inventory_tag_headers:
    root_scope_name: Default
    state: query 
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Assign annotations to a subnet
  tetration_inventory_tag_headers:
    root_scope_name: Default
    attribute: DeleteMe
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  description: a list of column headers 
  returned: always
  type: list 
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_COLUMN_NAMES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    ''' Main entry point for module execution
    '''
    # Module specific spec
    module_args = dict(
        root_scope_name=dict(type='str', required=True),
        attribute=dict(type='str', required=False),
        state=dict(type='str', required=True, choices=['absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ['state', 'absent', ['attribute']]
        ]
    )

    # These are all elements we put in our return JSON object for clarity
    tet_module = TetrationApiModule(module)
    result = {
        "object": None,
        "changed": False,
    }

    route = f"{TETRATION_COLUMN_NAMES}/{module.params['root_scope_name']}"
    current_headers = tet_module.run_method('GET', route)

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    if module.params['state'] == 'query':
        result['object'] = current_headers
    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif module.params['state'] == 'absent':
        if module.params['attribute'] in current_headers:
            delete_route = f"{route}/{module.params['attribute']}"
            result['object'] = tet_module.run_method('DELETE', delete_route)
            result['changed'] = True
        else:
            result['object'] = current_headers
    module.exit_json(**result)


if __name__ == '__main__':
    main()
