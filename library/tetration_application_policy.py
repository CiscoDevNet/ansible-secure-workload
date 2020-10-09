
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: tetration_application_policy

short description: Enables creation, deletion, and query of an application policy

version_added: '2.9'

description:
- Enables creation, deletion, and query of an application policy

options:
  app_id:
    description:
    - The id for the Application to which the policy belongs
    required: true
    type: string
  consumer_filter_id:
    description:
    - ID of a defined filter. Currently, user defined filter or scope
      can be used as the consumer of a policy
    - Mutually exclusive to C(consumer_filter_name)
    - Either C(consumer_filter_id) or C(consumer_filter_name) is required
    type: string
  consumer_filter_name:
    description:
    - Name of a defined filter. Currently, user defined filter or scope
      can be used as the consumer of a policy
    - Mutually exclusive to C(consumer_filter_id)
    - Either C(consumer_filter_id) or C(consumer_filter_name) is required
    type: string
  policy_action:
    description:
    - Possible values can be ALLOW or DENY. Indicates whether traffic should be allowed
      or dropped for the given service port/protocol between the consumer and provider
    - Required always
    required: true
    type: string
  priority:
    description: Used to sort policy
    required: true
    type: int
  provider_filter_id:
    description:
    - ID of a defined filter. Currently, user defined filter or scope
      can be used as the provider of a policy
    - Mutually exclusive to C(provider_filter_name)
    - Either C(provider_filter_id) or C(provider_filter_name) is required
    type: string
  provider_filter_name:
    description:
    - Name of a defined filter. Currently, user defined filter or scope
      can be used as the provider of a policy
    - Mutually exclusive to C(provider_filter_id)
    - Either C(provider_filter_id) or C(provider_filter_name) is required
    type: string
  rank:
    description:
    - 'Policy rank, possible values: DEFAULT or ABSOLUTE'
    required: true
    type: string
  state:
    choices: [present, absent, query]
    description: Add, remove or query for application policy
    required: true
    type: string
  version:
    description:
    - Indicates the version of the Application to which the policy belongs
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.
- Every parameter of this module is used to uniquely identify a policy
- Due to the above fact, this module can only add or delete a policy, no updates are possible

requirements:
- requests
- 'Required API Permission(s): app_policy_management'

author:
- Brandon Beck (@techbeck03)
- Joe Jacobs (@joej164)
'''

EXAMPLES = '''
# Add or modify application policy
tetration_application_policy:
    app_id: 59836821755f02724cbb54fb
    provider_filter_name: ACME:Example:Scope1
    consumer_filter_name: ACME:Example:Scope2
    version: v0
    rank: ABSOLUTE
    policy_action: ALLOW
    priority: 100
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete application policy
tetration_application_policy:
    app_id: 59836821755f02724cbb54fb
    provider_filter_name: ACME:Example:Scope1
    consumer_filter_name: ACME:Example:Scope2
    version: v0
    rank: ABSOLUTE
    policy_action: ALLOW
    priority: 100
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query for application policy
tetration_application_policy:
    app_id: 59836821755f02724cbb54fb
    provider_filter_name: ACME:Example:Scope1
    consumer_filter_name: ACME:Example:Scope2
    version: v0
    policy_action: ALLOW
    priority: 100
    rank: DEFAULT
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
    action:
      description: Action applied to the Policy
      returned: when C(state) is 'present' or 'query'
      type: str
    application_id:
      description: ID of the application the policy is associated with
      returned: when C(state) is 'present' or 'query'
      type: str
    consumer_filter:
      description: Details of the consumer filter applied to the policy
      returned: when C(state) is 'present' or 'query'
      type: complex
    consumer_filter_id:
      description: ID of the consumer filter applied to the policy
      returned: when C(state) is 'present' or 'query'
      type: str
    id:
      description: ID of the policy
      returned: when C(state) is 'present' or 'query'
      type: str
    l4_params:
      description: List of all the l4_params applied to the policy
      returned: when C(state) is 'present' or 'query'
      type: list
    priority:
      description: Priority of the policy
      returned: when C(state) is 'present' or 'query'
      type: int
    provider_filter:
      description: Details of the provider filter applied to the policy
      returned: when C(state) is 'present' or 'query'
      type: complex
    provider_filter_id:
      description: ID of the provider filter applied to the policy
      returned: when C(state) is 'present' or 'query'
      type: str
    rank:
      description: Category of the policy
      returned: when C(state) is 'present' or 'query'
      type: str
    version:
      description: Version of the application the policy is applied to
      returned: when C(state) is 'present' or 'query'
      type: str
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_INVENTORY_FILTER
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATION_POLICIES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    module_args = dict(
        app_id=dict(type='str', required=True),
        consumer_filter_id=dict(type='str', required=False),
        consumer_filter_name=dict(type='str', required=False),
        provider_filter_id=dict(type='str', required=False),
        provider_filter_name=dict(type='str', required=False),
        version=dict(type='str', required=True),
        rank=dict(type='str', required=True, choices=['DEFAULT', 'ABSOLUTE']),
        policy_action=dict(type='str', required=True, choices=['ALLOW', 'DENY']),
        priority=dict(type='int', required=True),
        state=dict(required=True, choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ['consumer_filter_id', 'consumer_filter_name'],
            ['provider_filter_id', 'provider_filter_name']
        ],
        required_one_of=[
            ['consumer_filter_id', 'consumer_filter_name'],
            ['provider_filter_id', 'provider_filter_name']
        ],
        required_if=[
            ['state', 'present', ['policy_action', 'priority']],
        ]
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': None,
    }

    # =========================================================================
    # Verify the application ID exists
    route = f"{TETRATION_API_APPLICATIONS}/{module.params['app_id']}"

    existing_app = tet_module.run_method('GET', route)

    if not existing_app:
        module.fail_json(msg='Unable to find existing application id')

    # Get the existing API Scopes and Inventory Filters to verify the consumer and provider settings
    existing_app_scopes = tet_module.run_method('GET', TETRATION_API_SCOPES)

    app_scope_name_to_scope_id = {}
    app_scope_name_to_parent_scope_id = {}

    for scope in existing_app_scopes:
        app_scope_name_to_scope_id[scope['name']] = scope['id']
        app_scope_name_to_parent_scope_id[scope['name']] = scope['parent_app_scope_id']

    existing_inventory_filters = tet_module.run_method('GET', TETRATION_API_INVENTORY_FILTER)

    # Build the inventory filter dict but check for duplicate entries and report them if found
    inv_filter_name_to_filter_id = {}
    duplicate_values = []
    for i in existing_inventory_filters:
        name = i['name']
        inv_id = i['id']
        if inv_id is None:
            module.fail_json(msg='An ID returned had a value of `None`')

        if inv_filter_name_to_filter_id.get(name) is None:
            inv_filter_name_to_filter_id[name] = inv_id
        else:
            duplicate_values.append(name)

    if duplicate_values:
        duplicate_values = set(duplicate_values)
        module.fail_json(
            msg=('The Tetration Server has multiple inventory filters with the same name.  '
                 'This is not supported with this module.  '
                 f'Duplicate names are: {duplicate_values}'))

    consumer_id = None
    provider_id = None

    if module.params['consumer_filter_id']:
        # Verify the ID is a valid api scope or an inventory filter
        if module.params['consumer_filter_id'] in app_scope_name_to_scope_id.values():
            consumer_id = module.params['consumer_filter_id']
        elif module.params['consumer_filter_id'] in inv_filter_name_to_filter_id.values():
            consumer_id = module.params['consumer_filter_id']
    elif module.params['consumer_filter_name']:
        # Verify the ID is a valid api scope or an inventory filter
        filter_name = module.params['consumer_filter_name']
        if app_scope_name_to_scope_id.get(filter_name):
            consumer_id = app_scope_name_to_scope_id[filter_name]
        elif inv_filter_name_to_filter_id.get(filter_name):
            consumer_id = inv_filter_name_to_filter_id[filter_name]

    if module.params['provider_filter_id']:
        # Verify the ID is a valid api scope or an inventory filter
        if module.params['provider_filter_id'] in app_scope_name_to_scope_id.values():
            provider_id = module.params['provider_filter_id']
        elif module.params['provider_filter_id'] in inv_filter_name_to_filter_id.values():
            provider_id = module.params['provider_filter_id']
    elif module.params['provider_filter_name']:
        # Verify the ID is a valid api scope or an inventory filter
        filter_name = module.params['provider_filter_name']
        if app_scope_name_to_scope_id.get(filter_name):
            provider_id = app_scope_name_to_scope_id[filter_name]
        elif inv_filter_name_to_filter_id.get(filter_name):
            provider_id = inv_filter_name_to_filter_id[filter_name]

    if consumer_id is None:
        module.fail_json(msg='The provided consumer name or id is invalid')

    if provider_id is None:
        module.fail_json(msg='The provided provider name or id is invalid')

    # Get the policies for the application
    if module.params['rank'] == 'ABSOLUTE':
        policy_route = f"{route}/absolute_policies"
    else:
        policy_route = f"{route}/default_policies"

    existing_policies = tet_module.run_method('GET', policy_route)

    # Now figure out if the policy defined in the module exists
    existing_policy = None
    existing_policy_id = None

    desired_unique_id = (module.params['priority'], module.params['policy_action'], consumer_id, provider_id)

    found_policies = []
    for policy in existing_policies:
        policy_id = (policy['priority'], policy['action'], policy['consumer_filter_id'], policy['provider_filter_id'])
        if policy_id == desired_unique_id:
            found_policies.append(policy)

    if len(found_policies) == 1:
        existing_policy = found_policies[0]
        existing_policy_id = found_policies[0]['id']
    elif len(found_policies) >= 2:
        module.fail_json(
            msg=("Multiple policies found with the given criteria.  "
                 "Cannot use this module if multiple policies match the "
                 "`priority`, `action`, `consumer`, and `provider` fields.  "
                 f"Duplicate policies: {found_policies}"))

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':
        if existing_policy:
            result['object'] = existing_policy
        else:
            req_payload = {
                "version": module.params['version'],
                "rank": module.params['rank'],
                "policy_action": module.params['policy_action'],
                "priority": module.params['priority'],
                "consumer_filter_id": consumer_id,
                "provider_filter_id": provider_id,
            }
            add_policy_route = f"{route}/policies"
            result['object'] = tet_module.run_method('POST', add_policy_route, req_payload=req_payload)
            result['changed'] = True

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif module.params['state'] == 'absent':
        if existing_policy:
            delete_policy_route = f"{TETRATION_API_APPLICATION_POLICIES}/{existing_policy_id}"

            result['object'] = tet_module.run_method('DELETE', delete_policy_route)
            result['changed'] = True

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif module.params['state'] == 'query':
        result['object'] = existing_policy

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
