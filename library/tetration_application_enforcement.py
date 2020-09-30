ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: tetration_application_enforcement

short_description: Enabled or disables application policy enforcement on a specified application workspace

version_added: '2.9'

description:
- Enabled or disables application policy enforcement on a specified application workspace

options:
  application_id:
    description: Application ID of application workspace targeted for enforcement
      state change.  Typically queried using tetration_application module
    required: true
    type: string
  state:
    choices: '[enabled, disabled]'
    description: Enable or Disable application policy enforcement
    required: true
    type: string
  version:
    default: None
    description: Optional version number of application policy
    type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the requests Python module.

requirements:
- requests

author:
  - Brandon Beck (@techbeck03)
  - Joseph Jacobs (@joej164)
'''

EXAMPLES = '''
# Enable application policy enforcement
tetration_application_enforcement:
    application_id: 5c93da83497d4f33d7145960
    state: enabled
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Enable application policy enforcement with specific version
tetration_application_enforcement:
    application_id: 5c93da83497d4f33d7145960
    version: 7
    state: enabled
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Disable application policy enforcement
tetration_application_enforcement:
    application_id: 5c93da83497d4f33d7145960
    state: disabled
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  contains:
    epoch: 
      description: Unique identifier for the latest enforcement profile. 
      returned: On Success
      sample: 5f70de34497d4f5ba2e6583c
      type: string
  description: the changed or modified object result, empty if no change
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    module_args = dict(
        application_id=dict(type='str', required=True),
        version=dict(type='str', required=False, default=None),
        state=dict(required=True, choices=['enabled', 'disabled']),
        provider=dict(type='dict', required=True, options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': None,
    }

    # =========================================================================
    # Get current state of the object
    app_route = f"{TETRATION_API_APPLICATIONS}/{module.params['application_id']}"
    existing_app = tet_module.run_method('GET', app_route)

    if not existing_app:
        module.fail_json(msg=f"Unable to find application with id: {module.params['application_id']}")

    # ---------------------------------
    # STATE == 'enabled'
    # ---------------------------------
    if module.params['state'] == 'enabled':
        if existing_app['enforcement_enabled'] is False:
            result['changed'] = True
        elif module.params['version'] is not None and existing_app['enforced_version'] != int(module.params['version'].strip('p')):
            # Per the API guide, the preferred method of passing the version is `p4` for Version 4
            # But the version returned from the api is just an int.  This deals with passing in an int or the p for for the version
            result['changed'] = True

        if result['changed']:
            req_payload = {}
            if module.params['version']:
                req_payload['version'] = module.params['version']

            route = f"{TETRATION_API_APPLICATIONS}/{module.params['application_id']}/enable_enforce"
            result['object'] = tet_module.run_method('POST', route, req_payload=req_payload)

    # ---------------------------------
    # STATE == 'disabled'
    # ---------------------------------
    elif module.params['state'] == 'disabled':
        result['changed'] = existing_app['enforcement_enabled']
        if result['changed']:
            route = f"{TETRATION_API_APPLICATIONS}/{module.params['application_id']}/disable_enforce"
            result['object'] = tet_module.run_method('POST', route)

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
