ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_inventory_filter

short_description: Add, remove, update, and query inventory filters

version_added: '2.8'

description:
- Enables management of Cisco Teetration inventory filters.
- Enables creation, modification, and deletion of filters.
- Enables management of complex filters with boolean operators on many different objects.

options:
  app_scope_id:
    description: Scope ID and scope name are mutually exclusive.
    type: string
  name:
    description:
    - Name of the inventory filter
    - When C(id) is not defined 
    required: False
    type: string
  id:
    description:
    - ID of the inventory filter
    - Required when C(name) is not defined 
    required: False
    type: string
  primary:
    default: 'false'
    description: When true it means inventory filter is restricted to ownership scope.
    type: bool
  public:
    default: 'false'
    description: When true the filter represents a service to be matched by other
      applications during application discovery runs (ADM).
    type: bool
  query_single:
    description:
    - Match Criteria associated with the scope
    - Supports only a single filter
    - Provides input validation
    - Mutually exclusive with [C(query_filter), C(query_nested)]
    type: dict
  query_filter:
    description:
    - Simple filter associated with the scope
    - Supports a single list of filters with one logical operator
    - Provides input validation
    - Mutually exclusive with [C(query_single), C(query_nested)]
    type: dict
  query_nested:
    description:
    - Complex filter associated with the scope
    - Supports deeply nested filter structures
    - Provides only top level input validation
    - Mutually exclusive with [C(query_single), C(query_filter)]
    type: dict
  state:
    choices: [present, absent, query]
    description: Add, change, or remove the inventory filter
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

author:
    - Doron Chosnek (@dchosnek)
    - Joe Jacobs(@joej164)

'''

EXAMPLES = '''
# Create a filter based on hostname
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: hostname contains dns
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_single:
      field: host_name
      type: contains
      value: dns

# Create a filter for a specific IP subnet
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: vpn users subnet
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_single:
      field: ip
      type: subnet
      value: 192.168.100.0/24

# Create filter for a user annotation field named Owner. When using a user
# annotation, the field value must always start with user_ and end with the
# name of the user annotation. user_Owner represents the user annotation
# named Owner.
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: owned by engineering
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_single:
      field: user_Owner
      type: eq
      value: engineering

# Create filter for a user annotation field named Location
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: location of Texas
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_single:
      field: user_Location
      type: contains
      value: Texas

# Create a filter based on interface name
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: interface eth0
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_single:
      field: iface_name
      type: eq
      value: eth0

# Create a filter based on interface MAC address
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: mac a9
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_single:
      field: iface_mac
      type: contains
      value: a9

# Create a filter based on different operating system types 
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: Various types of Operating Systems
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    query_filter:
      filter:
        - field: os 
          type: contains 
          value: linux 
        - field: os 
          type: contains 
          value: windows
        - field: os 
          type: contains 
          value: mac
      type: or

# Build a complex filter with both 'and' and 'or' statements
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: vulnerable linux and windows hosts
    app_scope_id: 5ce71503497d4f2c23af8aaa
    state: present
    public: true
    primary: true
    query_nested:
      filters:
        - field: os
          type: contains
          value: linux
        - field: os
          type: contains
          value: windows 
        - filters:
            - field: host_tags_cvss3
              type: gt
              value: 8
            - field: host_tags_cvss2
              type: gt
              value: 8
          type: or
      type: or

# Delete some inventory filters
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: "{{ item }}"
    app_scope_name: Default
    state: absent
loop:
- my first filter
- my second filter
'''

RETURN = '''
object:
  contains:
    app_scope_id:
      description: ID of the scope associated with the filter
      returned: when C(state) is present or query
      sample: 5bdf9776497d4f397d38fdcb
      type: dict
    id:
      description: Unique identifier for the inventory filter
      returned: when C(state) is present or query
      sample: 5be671e9497d4f08f028b1bb
      type: dict
    name:
      description: User specified name of the inventory filter
      returned: when C(state) is present or query
      type: string
    primary:
      description: When true it means inventory filter is restricted to ownership
        scope
      returned: when C(state) is present or query
      sample: 'false'
      type: bool
    public:
      description: When true the filter represents a service to be matched by other
        applications during application discovery runs (ADM).
      returned: when C(state) is present or query
      sample: 'false'
      type: bool
    query:
      description: Filter (or match criteria) associated with the filter in conjunction
        with the filters of the parent scopes.
      returned: when C(state) is present or query
      type: dict
    short_query:
      description: Filter (or match criteria) associated with the filter only.
      returned: when C(state) is present or query
      type: dict
    updated_at:
      description: Unix timestamp for the last update of the filter
      returned: when C(state) is present or query
      sample: 1541829226
      type: int
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_INVENTORY_FILTER
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    single_filter = dict(
        field=dict(type='str', required=True),
        type=dict(type='str', required=True),
        value=dict(type='str', required=True)
    )

    query_filter_structure = dict(
        filters=dict(type='list', elements='dict', options=single_filter, required=True),
        type=dict(type='str', required=True)
    )

    nested_query_filter_structure = dict(
        filters=dict(type='list', elements='dict', required=True),
        type=dict(type='str', required=True)
    )

    module_args = dict(
        name=dict(type='str', required=False),
        id=dict(type='str', required=False),
        query_filter=dict(type='dict', options=query_filter_structure, required=False),
        query_nested=dict(type='dict', options=nested_query_filter_structure, required=False),
        query_single=dict(type='dict', options=single_filter, reqired=False),
        app_scope_id=dict(type='str', required=False),
        primary=dict(type='bool', required=False, default=False),
        public=dict(type='bool', required=False, default=False),
        state=dict(choices=['present', 'absent', 'query'], required=True),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    result = {
        'changed': False,
        'object': {}
    }

    result_obj = {}

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['name', 'id'],
        ],
        mutually_exclusive=[
            ['query_filter', 'query_nested', 'query_single']
        ],
        required_by={
            'name': ['app_scope_id']
        }
    )

    # Get current state of the object
    tet_module = TetrationApiModule(module)

    all_scopes_response = tet_module.run_method('GET', TETRATION_API_SCOPES)
    all_scopes_lookup = {s['id'] for s in all_scopes_response}

    all_inventory_filters_response = tet_module.run_method('GET', TETRATION_API_INVENTORY_FILTER)
    all_inventory_filters_lookup = {(s['name'], s['app_scope_id']): s['id'] for s in all_inventory_filters_response}

    unique_inventory_filter_name = module.params['name'], module.params['app_scope_id']

    # Since the query parameter data all goes into one field eventually, just extract it into
    # A value here for use later on in the module
    query_parameters = ['query_filter', 'query_nested', 'query_single']
    extracted_query_filter = {}
    for query in query_parameters:
        if module.params[query]:
            extracted_query_filter = module.params[query]

    # Validate items that should exist do exist
    if module.params['id'] and module.params['id'] not in all_inventory_filters_lookup.values():
        error_message = "`id` passed into the module does not exist."
        module.fail_json(msg=error_message, searched_filter_id=module.params['id'])

    if module.params['app_scope_id'] and module.params['app_scope_id'] not in all_scopes_lookup:
        error_message = "`app_scope_id` passed into the module does not exist."
        module.fail_json(msg=error_message)

    if module.params['state'] == 'present':
        if module.params['id'] or unique_inventory_filter_name in all_inventory_filters_lookup.keys():
            # Object exists, going to see if updates are needed
            if module.params['id']:
                inv_filter_to_update = module.params['id']
            else:
                inv_filter_to_update = all_inventory_filters_lookup[unique_inventory_filter_name]

            route = f"{TETRATION_API_INVENTORY_FILTER}/{inv_filter_to_update}"
            response = tet_module.run_method('GET', route)

            req_payload = {
                'name': None,
                'query': {},
                'app_scope_id': None,
                'primary': None,
                'public': None
            }

            # Updating the Update Object
            payload_keys = [k for k in req_payload.keys()]
            for key in payload_keys:
                if module.params.get(key) != None and module.params[key] != response[key]:
                    req_payload[key] = module.params[key]
                elif key == 'query':
                    if extracted_query_filter and extracted_query_filter != response['short_query']:
                        req_payload[key] = extracted_query_filter
                    else:
                        req_payload.pop(key)
                else:
                    req_payload.pop(key)

            if req_payload:
                update_response = tet_module.run_method('PUT', route, req_payload=req_payload)
                result['changed'] = True
                result_obj = update_response
            else:
                result_obj = response

        elif unique_inventory_filter_name not in all_inventory_filters_lookup.keys():
            # Object does not exist, going to create it
            if not extracted_query_filter:
                error_message = (
                    'In order to create a new `inventory_filter` you must also have a `query` parameter defined.'
                )
                module.fail_json(msg=error_message)

            req_payload = {
                'name': module.params['name'],
                'query': extracted_query_filter,
                'app_scope_id': module.params['app_scope_id'],
                'primary': module.params['primary'],
                'public': module.params['public']
            }
            response = tet_module.run_method('POST', TETRATION_API_INVENTORY_FILTER, req_payload=req_payload)
            result_obj = response
            result['changed'] = True

    if module.params['state'] == 'absent':
        if module.params['id']:
            delete_id = module.params['id']
        else:
            delete_id = all_inventory_filters_lookup.get(unique_inventory_filter_name)

        if delete_id:
            route = f"{TETRATION_API_INVENTORY_FILTER}/{delete_id}"
            response = tet_module.run_method('DELETE', route)
            result_obj = response
            result['changed'] = True

    if module.params['state'] == 'query':

        if module.params['id']:
            search_id = module.params['id']
        else:
            if unique_inventory_filter_name in all_inventory_filters_lookup.keys():
                search_id = all_inventory_filters_lookup[unique_inventory_filter_name]
            else:
                search_id = None

        if search_id:
            route = f"{TETRATION_API_INVENTORY_FILTER}/{search_id}"
            response = tet_module.run_method('GET', route)
            result_obj = response

    result['object'] = result_obj

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
