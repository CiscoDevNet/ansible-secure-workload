
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: tetration_application_policy_catchall

short description: Allows the updating and querying of an applications catchall value

version_added: '2.9'

description:
- Enables setting the catchall value of an application to `ALLOW` or `DENY`

options:
  app_id:
    description:
    - The id for the Application to which the policy belongs
    type: string
  policy_action:
    description:
    - Possible values can be ALLOW or DENY. Indicates whether traffic should be allowed
      or dropped for the given service port/protocol between the consumer and provider
    type: string
  state:
    description:
    - Whether to update or just query the catchall policy of the application
    type: string
  version:
    description:
    - Indicates the version of the Application to which the policy belongs
    type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.

requirements:
- requests
- 'Required API Permission(s): app_policy_management'

author:
- Joe Jacobs (@joej164)
'''

EXAMPLES = '''
# Set the catchall policy to ALLOW for an application
tetration_application_policy_catchall:
    app_id: 59836821755f02724cbb54fb
    version: v0
    policy_action: ALLOW
    state: update
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Set the catchall policy to DENY for an application
tetration_application_policy_catchall:
    app_id: 59836821755f02724cbb54fb
    version: v0
    policy_action: DENY
    state: update
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query the catchall policy for an application
tetration_application_policy_catchall:
    app_id: 59836821755f02724cbb54fb
    version: v0
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
      description: current state of the applications catcahall policy
      returned: always
      type: string
    application_id:
      description: application id of the catch all policy modified
      returned: always
      type: string
    id:
      description: id of the catch all policy
      returned: always
      type: string
    rank:
      description:
      - type of policy returned
      - should always be `CATCH_ALL`
      returned: always
      type: string
    version:
      description: version of the application id updated
      returned: always
      type: string
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    module_args = dict(
        app_id=dict(type='str', required=True),
        version=dict(type='str', required=True),
        policy_action=dict(type='str', required=False, choices=['ALLOW', 'DENY']),
        state=dict(required=True, choices=['update', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ['state', 'update', ['policy_action']]
        ]
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': None,
    }

    route = f"{TETRATION_API_APPLICATIONS}/{module.params['app_id']}/catch_all"
    get_payload = {
        'version': module.params['version'],
    }

    existing_policy = tet_module.run_method('GET', route, req_payload=get_payload)

    # Valid inputs are the version number or the version number prefixed with the letter `v`
    # this next step creates all possible versions for comparision
    possible_versions = [module.params['version'], f"v{module.params['version']}"]
    if existing_policy['version'] not in possible_versions:
        module.fail_json(msg="The application id and policy entered do not exist")

    if module.params['state'] == 'update':
        payload = {
            'version': module.params['version'],
            'policy_action': module.params['policy_action']
        }

        if existing_policy['action'] != module.params['policy_action']:
            result['changed'] = True

        api_results = tet_module.run_method('PUT', route, req_payload=payload)

        result['object'] = api_results
    else:
        result['object'] = existing_policy

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
