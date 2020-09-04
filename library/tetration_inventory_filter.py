ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_inventory_filter

short_description: Add, remove, and update inventory filters

version_added: '2.8'

description:
- Enables management of Cisco Teetration inventory filters.
- Enables creation, modification, and deletion of filters.
- Enables management of complex filters with boolean operators on many different objects.

options:
  app_scope_id:
    description: Scope ID and scope name are mutually exclusive.
    type: string
  app_scope_name:
    description: Scope ID and scope name are mutually exclusive.
    type: string
  name:
    description: Name of the inventory filter
    required: true
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
  query:
    description: Filter (or match criteria) associated with the scope
    type: dict
  state:
    choices: '[present, absent, query]'
    description: Add, change, or remove the inventory filter
    required: true
    type: string

extends_documentation_fragment: tetration

author:
    - Doron Chosnek (@dchosnek)
    - Joe Jacobs(@joej164)

'''

EXAMPLES = '''
# Create a filter based on hostname
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: hostname contains dns
    app_scope_name: Default
    state: present
    query:
    field: host_name
    type: contains
    value: dns

# Create a filter for a specific IP subnet
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: vpn users subnet
    app_scope_name: Default
    state: present
    query:
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
    app_scope_name: Default
    state: present
    query:
    field: user_Owner
    type: eq
    value: engineering

# Create filter for a user annotation field named Location
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: location of Texas
    app_scope_name: Default
    state: present
    query:
    field: user_Location
    type: contains
    value: Texas

# Create a filter based on interface name
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: interface eth0
    app_scope_name: Default
    state: present
    query:
    field: iface_name
    type: eq
    value: eth0

# Create a filter based on interface MAC address
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: mac a9
    app_scope_name: Default
    state: present
    query:
    field: iface_mac
    type: contains
    value: a9

# Build a complex filter with both 'and' and 'or' statements
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: vulnerable linux hosts
    app_scope_name: Default
    state: present
    public: true
    primary: true
    query:
    type: and
    filters:
    - field: os
        type: contains
        value: linux
    - type: or
        filters:
        - field: host_tags_cvss3
        type: gt
        value: 8
        - field: host_tags_cvss2
        type: gt
        value: 8

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

    result = dict(
        changed=False,
        object={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['name', 'id'],
        ],
        mutually_exclusive=[
            ['name', 'id'],
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

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
