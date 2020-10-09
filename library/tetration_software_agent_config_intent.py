ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tetration_software_agent_config_intent

short description: Enables creation, deletion and query of software agent config intent

version_added: '2.9'

description:
- Enables creation, deletion and query of software agent config intent

options:
  inventory_config_profile_id:
    description: ID of inventory config profile
    required: true
    type: string
  inventory_filter_id:
    description:
    - ID of inventory filter for associating agent profile
    - Require one of [C(scope_id), C(inventory_filter_name), C(inventory_filter_id)]
    - Mutually exclusive to C(inventory_filter_name)
    type: string
  inventory_filter_name:
    description:
    - Name of inventory filter for associating agent profile
    - Require one of [C(scope_id), C(inventory_filter_name), C(inventory_filter_id)]
    - Mutually exclusive to C(inventory_filter_id)
    - Required together [C(inventory_filter_name), C(inventory_filter_type)]
    type: string
  inventory_filter_type:
    choices: [inventory, scope]
    description:
    - Type of inventory filter used for association
    - Required together [C(inventory_filter_name), C(inventory_filter_type)]
    type: string
  root_app_scope_id:
    description: ID of root app scope for tenant to which an agent profile should
      be applied
    type: string
  state:
    choices: [present, absent, query]
    default: present
    description: Add, change, remove or query for agent config intents
    required: true
    type: string
  tenant_name:
    description: Tenant name to which an agent config profile should be applied
    type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.

requirements:
- requests
- 'Required API Permission(s): sensor_management'

author:
- Brandon Beck (@techbeck03)
- Joe Jacobs (@joej164)

'''

EXAMPLES = '''
# Add or Modify agent config intent
tetration_software_agent_config_intent:
    profile_id: 596d6751497d4f3eb1f1fd2d
    filter_id: 596d6751497d4f3eb1f1abc
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
# Delete agent config intent
tetration_software_agent_config_intent:
    profile_name: ACME Profile
    filter_name: ACME Filter or Scope
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
# Query agent config intent
tetration_software_agent_config_intent:
    profile_name: ACME Profile
    filter_name: ACME Filter or Scope
    state: query
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  contains:
    created_at:
      description: Date this inventory was created (Unix Epoch)
      returned: when C(state) is present or query
      sample: 1500402190
      type: int
    id:
      description: Unique identifier for the agent config intent
      returned: when C(state) is present or query
      sample: 2000
      type: int
    intentory_config_profile_id:
      description: Unique ID of agent config profile
      returned: when C(state) is present or query
      sample: 596d6751497d4f3eb1f1fd2d
      type: string
    inventory_filter_id:
      description: Unique id of the filter associated with intent
      returned: when C(state) is present or query
      sample: 5c493b58755f027da9818750
      type: string
    name:
      description: Null value
      returned: when C(state) is present or query
      sample: Null
      type: string
    updated_at:
      description: Date this inventory filter was last updated (Unix Epoch)
      returned: when C(state) is present or query
      sample: 1500402190
      type: int
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_AGENT_CONFIG_PROFILES
from ansible.module_utils.tetration_constants import TETRATION_API_AGENT_CONFIG_INTENTS
from ansible.module_utils.tetration_constants import TETRATION_API_INVENTORY_FILTER
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    # Main entry point for module execution

    # Module specific spec
    module_args = dict(
        profile_name=dict(type='str', required=False),
        profile_id=dict(type='str', required=False),
        filter_id=dict(type='str', required=False),
        filter_name=dict(type='str', required=False),
        state=dict(default='present', choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['profile_name', 'profile_id'],
            ['filter_id', 'filter_name'],
        ],
        mutually_exclusive=[
            ['profile_name', 'profile_id'],
            ['filter_id', 'filter_name'],
        ]
    )

    # These are all elements we put in our return JSON object for clarity
    tet_module = TetrationApiModule(module)
    result = {
        'changed': False,
        'object': {},
    }

    # =========================================================================
    # Get current state of the object
    config_profiles = tet_module.run_method('GET', TETRATION_API_AGENT_CONFIG_PROFILES)
    config_profiles_and_ids = {c['name']: c['id'] for c in config_profiles}

    profile_id = None
    if module.params['profile_id'] in config_profiles_and_ids.values():
        profile_id = module.params['profile_id']
    elif module.params['profile_name'] in config_profiles_and_ids.keys():
        profile_name = module.params['profile_name']
        profile_id = config_profiles_and_ids[profile_name]

    if not profile_id:
        if module.params['profile_id']:
            module.fail_json(msg=f"Unable to find existing profile id: {module.params['profile_id']}")
        else:
            module.fail_json(msg=f"Unable to find existing profile named: {module.params['profile_name']}")

    # Get the existing API Scopes and Inventory Filters to verify the filter parameters passed in
    existing_app_scopes = tet_module.run_method('GET', TETRATION_API_SCOPES)

    # Build a lookup object for the app scopes
    app_scope_name_to_scope_id = {s['name']: s['id'] for s in existing_app_scopes}

    # Build the inventory filter dict but check for duplicate entries and report them if found
    existing_inventory_filters = tet_module.run_method('GET', TETRATION_API_INVENTORY_FILTER)

    inv_filter_name_to_filter_id = {}
    duplicate_values = []
    for i in existing_inventory_filters:
        name = i['name']
        inv_id = i['id']
        if inv_id is None:      # If the API returns an ID of None, this code won't work
            module.fail_json(msg='An ID returned had a value of `None`')

        if inv_filter_name_to_filter_id.get(name) is None:      # Does the ID exist in the new dict
            inv_filter_name_to_filter_id[name] = inv_id
        else:
            duplicate_values.append(name)

    if duplicate_values:
        duplicate_values = set(duplicate_values)
        module.fail_json(
            msg=('The Tetration Server has multiple inventory filters with the same name.  '
                 f'This is not supported with this module.  Duplicate names are: {duplicate_values}'))

    filter_id = None

    if module.params['filter_id']:
        # Verify the ID is a valid api scope or an inventory filter
        if module.params['filter_id'] in app_scope_name_to_scope_id.values():
            filter_id = module.params['filter_id']
        elif module.params['filter_id'] in inv_filter_name_to_filter_id.values():
            filter_id = module.params['filter_id']
    elif module.params['filter_name']:
        # Verify the ID is a valid api scope or an inventory filter
        filter_name = module.params['filter_name']
        if app_scope_name_to_scope_id.get(filter_name):
            filter_id = app_scope_name_to_scope_id[filter_name]
        elif inv_filter_name_to_filter_id.get(filter_name):
            filter_id = inv_filter_name_to_filter_id[filter_name]

    if filter_id is None:
        module.fail_json(msg='The provided filter name or id is invalid')

    # Get the current config intents
    existing_intents = tet_module.run_method('GET', TETRATION_API_AGENT_CONFIG_INTENTS)

    intent_to_find = {
        'inventory_config_profile_id': profile_id,
        'inventory_filter_id': filter_id
    }

    existing_intent = None
    for intent in existing_intents:
        if tet_module.is_subset(intent_to_find, intent):
            existing_intent = intent

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':
        new_object = {
            'inventory_config_profile_id': profile_id,
            'inventory_filter_id': filter_id
        }

        if not existing_intent:
            result['object'] = tet_module.run_method('POST', TETRATION_API_AGENT_CONFIG_INTENTS, req_payload=new_object)
            result['changed'] = True
        else:
            result['object'] = existing_intent

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif module.params['state'] in 'absent':
        if existing_intent:
            route = f"{TETRATION_API_AGENT_CONFIG_INTENTS}/{existing_intent['id']}"
            result['object'] = tet_module.run_method('DELETE', route)
            result['changed'] = True

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    else:
        if existing_intent:
            result['object'] = existing_intent

    module.exit_json(**result)


if __name__ == '__main__':
    main()
