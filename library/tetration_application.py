ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: tetration_application

short description: Enables creation, modification, deletion and query of an application

version_added: '2.8'

description:
- Enables creation, modification, deletion and query of an application

options:
  alternate_query_mode:
    description: Indicates if dynamic mode is used for the application. In the dynamic
      mode, an ADM run creates one or more candidate queries for each cluster. Default
      value is false
    type: bool
  app_id:
    description:
    - The id for the Application
    - Require one of [C(app_name), C(app_id)]
    - Mutually exclusive to C(app_name)
    type: string
  app_name:
    description:
    - The name for the Application
    - Require one of [C(app_name), C(app_id)]
    - Mutually exclusive to C(app_id)
    type: string
  app_scope_id:
    description:
    - The id for the Scope associated with the application
    - Require one of [C(app_scope_name), C(app_scope_id), C(app_id)]
    - Mutually exclusive to C(app_scope_name)
    type: string
  app_scope_name:
    description:
    - The name for the Scope associated with the application
    - Require one of [C(app_scope_name), C(app_scope_id), C(app_id)]
    - Mutually exclusive to C(app_scope_id)
    type: string
  description:
    description: User specified description of the application
    type: string
  strict_validation:
    description:
    - Will return an error if there are unknown keys/attributes in the uploaded data.
    - Useful for catching misspelled keys.
    - Default value is false.
    type: bool
  primary:
    description: Indicates if the application is primary for its scope
    type: bool
  state:
    choices: '[present, absent]'
    description: Add, change, remove or query for application
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the requests Python module.
- Only the fields C(app_name), C(description), C(primary) can be updated on an existing application

requirements: 
- requests 

author:
    - Brandon Beck (@techbeck03)
    - Joseph Jacobs (@joej164)
'''

EXAMPLES = '''
# Add or Modify application
tetration_application:
    app_name: ACME InfoSec Policies
    app_scope_name: ACME:Example:Application
    description: InfoSec Policies for Acme Application
    primary: yes
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete application
tetration_application:
    app_name: ACME InfoSec Policies
    app_scope_name: ACME:Example:Application
    primary: yes
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  contains:
    alternate_query_mode:
      description: Indicates if dynamic mode is used for the application
      returned: when C(state) is present or query
      sample: 'false'
      type: bool
    app_scope_id:
      description: Unique identifier of app scope associated with application workspace
      returned: when C(state) is present or query
      sample: 596d5215497d4f3eaef1fd04
      type: int
    author:
      description: Author of application workspace
      returned: when C(state) is present or query
      sample: Brandon Beck
      type: string
    created_at:
      description: Date this application was created (Unix Epoch)
      returned: when C(state) is present or query
      sample: 1500402190
      type: string
    description:
      description: A description for the application
      returned: when C(state) is present or query
      sample: Security policies for my application
      type: string
    enforced_version:
      description: The policy version to enforce
      returned: when C(state) is present or query
      sample: 7
      type: int
    enforcement_enabled:
      description: Sets whether enforcement is enabled on this application
      returned: when C(state) is present or query
      sample: 'true'
      type: bool
    id:
      description: Unique identifier for the application workspace
      returned: when C(state) is present or query
      sample: 5c93da83497d4f33d7145960
      type: int
    latest_adm_version:
      description: Latest policy version
      returned: when C(state) is present or query
      sample: 8
      type: int
    name:
      description: Name of application workspace
      returned: when C(state) is present or query
      sample: My Application Policy
      type: string
    primary:
      description: Sets whether this application should be primary for the given scope
      returned: when C(state) is present or query
      sample: 'true'
      type: bool
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    module_args = dict(
        app_name=dict(type='str', required=False),
        app_id=dict(type='str', required=False),
        app_scope_id=dict(type='str', required=False),
        app_scope_name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        alternate_query_mode=dict(type='bool', required=False, default=False),
        strict_validation=dict(type='bool', required=False, default=False),
        primary=dict(type='bool', required=False),
        state=dict(required=True, choices=['present', 'absent']),
        provider=dict(type='dict', required=True, options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ['app_scope_name', 'app_scope_id']
        ],
        required_one_of=[
            ['app_name', 'app_id'],
        ],
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': None,
    }

    # =========================================================================
    # Verify passed in data is accurate.
    existing_app_scope = {}
    if module.params['app_scope_id']:
        app_scope_route = f"{TETRATION_API_SCOPES}/{module.params['app_scope_id']}"
        existing_app_scope = tet_module.run_method('GET', app_scope_route)
        if not existing_app_scope:
            module.fail_json(msg=f"Unable to find existing app with the id of: {module.params['app_scope_id']}")
    elif module.params['app_scope_name']:
        all_scopes = tet_module.run_method('GET', TETRATION_API_SCOPES)
        found_app_scopes = [scope for scope in all_scopes if scope['name'] == module.params['app_scope_name']]
        if len(found_app_scopes) == 0:
            module.fail_json(
                msg=f"There were no app scopes that matched the name entered.  Searched for: {module.params['app_scope_name']}")
        elif len(found_app_scopes) > 1:
            module.fail_json(
                msg=f"There were too many app scopes that matched the name entered.  Searched for: {module.params['app_scope_name']}")
        existing_app_scope = found_app_scopes[0]

    existing_app = {}
    if module.params['app_id']:
        app_route = f"{TETRATION_API_APPLICATIONS}/{module.params['app_id']}"
        existing_app = tet_module.run_method('GET', app_route)
        if not existing_app:
            module.fail_json(msg=f"The App ID entered is not in the system.  Searched for: {module.params['app_id']}")
    elif module.params['app_name']:
        # If we have an app_id, and it's valid, we don't care about searching for the app_id by name
        # If we don't have an app_id, then we need to find an app, but it's ok if one doesn't exist
        # because we'll then make it, or we could be verifying it's absent
        apps = tet_module.run_method('GET', TETRATION_API_APPLICATIONS)
        found_apps = [found for found in apps if found['name'] == module.params['app_name']]
        if len(found_apps) > 1:
            module.fail_json(
                msg=f"There were too many apps that matched the name entered.  Searched for: {module.params['app_name']}")
        elif len(found_apps) == 1:
            existing_app = found_apps[0]

    app_route = ""
    if existing_app:
        app_route = f"{TETRATION_API_APPLICATIONS}/{existing_app['id']}"

    # =========================================================================
    # Now enforce the desired state (present, absent)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':
        # if the object does not exist at all, create it but verify we have all needed data first
        if not existing_app and not existing_app_scope:
            module.fail_json(msg="The application does not exist.  Must provide a Scope ID or Scope Name to create a new scope.")

        if not existing_app and not module.params['primary']:
            module.fail_json(
                msg="The application does not exist.  Must provide info on if the scope is primary or not when creating a scope.")

        if existing_app:
            updated_app = {
                'name': module.params['app_name'],
                'description': module.params['description'],
                'primary': module.params['primary']
            }
            if not module.params['app_name']:
                updated_app.pop('name')
            if module.params['description'] is None:
                updated_app.pop('description')
            if module.params['primary'] is None:
                updated_app.pop('primary')

            is_subset = tet_module.is_subset(updated_app, existing_app)

            if not is_subset:
                result['object'] = tet_module.run_method('PUT', app_route, req_payload=updated_app)
                result['changed'] = True
            else:
                result['object'] = existing_app
        else:
            new_app = {
                'app_scope_id': existing_app_scope['id'],
                'name': module.params['app_name'],
                'description': module.params['description'],
                'alternate_query_mode': module.params['alternate_query_mode'],
                'strict_validation': module.params['strict_validation'],
                'primary': module.params['primary']
            }

            result['object'] = tet_module.run_method("POST", TETRATION_API_APPLICATIONS, req_payload=new_app)
            result['changed'] = True

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif module.params['state'] == 'absent':
        if existing_app:
            if existing_app['enforcement_enabled']:
                module.fail_json(
                    msg='Cannot delete workspace with enforcement enabled.  Disable enforcement before deleting')
            elif existing_app['primary']:
                module.fail_json(
                    msg='Cannot delete primary application.  Try making application secondary before deleting')

            result['object'] = tet_module.run_method('DELETE', app_route)
            result['changed'] = True

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
