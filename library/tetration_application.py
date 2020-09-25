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
  force:
    description: If set to True will allow removing workspace with enforcement enabled
    type: bool
  primary:
    description: Indicates if the application is primary for its scope
    type: bool
  query_level:
    choices: '[top, details]'
    default: top
    description: The level of detail of returned query data
    type: string
  query_type:
    choices: '[single, scope, tenant]'
    default: single
    description: Options for expanding query search
    type: string
  state:
    choices: '[present, absent, query]'
    description: Add, change, remove or query for application
    required: true
    type: string
  strict_validation:
    description: Unix timestamp of when the application was created (Epoch Timestamp)
    type: bool

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the requests Python module.
- Supports check mode.

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
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete application
tetration_application:
    app_name: ACME InfoSec Policies
    app_scope_name: ACME:Example:Application
    primary: yes
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query for application details
tetration_application:
    app_name: ACME InfoSec Policies
    app_scope_name: ACME:Example:Application
    query_type: single
    query_level: details
    state: query
    provider:
      host: "tetration-cluster@company.com"
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
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration.api import TETRATION_API_SCOPES

from ansible.utils.display import Display
display = Display()

from time import sleep


def main():
    tetration_spec = dict(
        app_name=dict(type='str', required=False),
        app_id=dict(type='str', required=False),
        app_scope_id=dict(type='str', required=False),
        app_scope_name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        alternate_query_mode=dict(type='bool', required=False, default=False),
        strict_validation=dict(type='bool', required=False, default=False),
        primary=dict(type='bool', required=False, default=True),
        force=dict(type='bool', required=False, default=False),
        query_type=dict(type='str', required=False, choices=['single', 'scope', 'tenant'], default='single'),
        query_level=dict(type='str', choices=['top', 'details'], default='top')
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(required=True, choices=['present', 'absent', 'query'])
    )

    argument_spec.update(tetration_spec)
    argument_spec.update(TetrationApiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ['app_scope_name', 'app_scope_id'],
        ],
        required_one_of=[
            # ['app_name', 'app_id'],
            ['app_scope_name', 'app_scope_id'],
        ],
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = dict(
        changed=False,
        object=None,
    )

    state = module.params['state']
    app_name = module.params['app_name']
    app_id = module.params['app_id']
    app_scope_name = module.params['app_scope_name']
    app_scope_id = module.params['app_scope_id']
    description = module.params['description']
    alternate_query_mode = module.params['alternate_query_mode']
    strict_validation = module.params['strict_validation']
    primary = module.params['primary']
    force = module.params['force']
    query_type = module.params['query_type']
    query_level = module.params['query_level']
    existing_app = None
    existing_app_scope = None

    # =========================================================================
    # Get current state of the object
    if app_scope_id:
        existing_app_scope = tet_module.run_method(
            method_name='get',
            target='%s/%s' % (TETRATION_API_SCOPES, app_scope_id)
        )
    elif not app_scope_id:
        existing_app_scope = tet_module.get_object(
            target=TETRATION_API_SCOPES,
            filter=dict(name=app_scope_name)
        )

    if not existing_app_scope:
        module.fail_json(msg='Unable to find existing app scope named: %s' % app_scope_name)

    if app_id:
        existing_app = tet_module.run_method(
            method_name='get',
            target='%s/%s' % (TETRATION_API_APPLICATIONS, app_id)
        )
    elif not app_id:
        existing_app = tet_module.get_object(
            target=TETRATION_API_APPLICATIONS,
            filter=dict(name=app_name, app_scope_id=existing_app_scope['id'])
        )
    # =========================================================================
    # Now enforce the desired state (present, absent, query)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':

        # if the object does not exist at all, create it
        new_object = dict(
            app_scope_id=existing_app_scope['id'],
            name=app_name,
            description=description,
            alternate_query_mode=alternate_query_mode,
            primary=primary,
        )
        if existing_app:
            new_object['id'] = existing_app['id']
            result['changed'] = tet_module.filter_object(new_object, existing_app, check_only=True)
            if result['changed']:
                if not module.check_mode:
                    del new_object['id']
                    tet_module.run_method(
                        method_name='put',
                        target='%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id']),
                        req_payload=dict(
                            name=app_name,
                            description=description,
                            primary=primary
                        )
                    )
                else:
                    result['object'] = new_object
        else:
            if not module.check_mode:
                new_object['strict_validation'] = strict_validation,
                app_object = tet_module.run_method(
                    method_name='post',
                    target=TETRATION_API_APPLICATIONS,
                    req_payload=new_object
                )
                existing_app = dict(id=app_object['id'])
            result['changed'] = True

        # if the object does exist, check to see if any part of it should be
        # changed
        if result['changed']:
            if not module.check_mode:
                result['object'] = tet_module.run_method(
                    method_name='get',
                    target='%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id'])
                )
            else:
                result['object'] = new_object
        else:
            result['changed'] = False
            result['object'] = existing_app

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif state == 'absent':
        if existing_app:
            if existing_app['enforcement_enabled'] and not force:
                module.fail_json(
                    msg='Cannot delete workspace with enforcement.  Try disabling enforcement or use the force option')
            elif existing_app['primary'] and not force:
                module.fail_json(
                    msg='Cannot delete primary application.  Try making application secondary or use the force option')
            elif existing_app['primary'] and force:
                if existing_app['enforcement_enabled']:
                    tet_module.run_method(
                        method_name='post',
                        target='%s/%s/disable_enforce' % (TETRATION_API_APPLICATIONS, existing_app['id'])
                    )
                    sleep(10)
                tet_module.run_method(
                    method_name='put',
                    target='%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id']),
                    req_payload=dict(
                        name=app_name,
                        description=description,
                        primary=False
                    )
                )
                sleep(2)
            result['changed'] = True
            if not module.check_mode:
                tet_module.run_method(
                    method_name='delete',
                    target='%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id'])
                )

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif state == 'query':
        if query_type == 'tenant':
            if existing_app_scope['id'] != existing_app_scope['root_app_scope_id']:
                module.fail_json(msg='query_type `tenant` is only allowed on root scopes')
            app_scopes = tet_module.get_object(
                target=TETRATION_API_SCOPES,
                filter=dict(root_app_scope_id=existing_app_scope['root_app_scope_id']),
                allow_multiple=True
            )
            scope_ids = [scope['id'] for scope in app_scopes]
            applications = tet_module.run_method(
                method_name='get',
                target=TETRATION_API_APPLICATIONS
            )
            if applications:
                applications = [valid_item for valid_item in applications if valid_item['app_scope_id'] in scope_ids]
            if query_level == 'details':
                app_details = []
                for application in applications:
                    app_details.append(
                        tet_module.run_method(
                            method_name='get',
                            target='%s/%s/details' % (TETRATION_API_APPLICATIONS, application['id'])
                        )
                    )
                result['object'] = app_details
            else:
                result['object'] = applications if applications else []
        elif query_type == 'scope':
            applications = tet_module.run_method(
                method_name='get',
                target=TETRATION_API_APPLICATIONS,
            )
            if applications:
                applications = [valid_item for valid_item in applications if valid_item['app_scope_id']
                                == existing_app_scope['id']]
            if query_level == 'details':
                app_details = []
                for application in applications:
                    app_details.append(
                        tet_module.run_method(
                            method_name='get',
                            target='%s/%s/details' % (TETRATION_API_APPLICATIONS, application['id'])
                        )
                    )
                result['object'] = app_details
            else:
                result['object'] = applications if applications else []
        else:
            if query_level == 'details':
                existin_app = []
                app_details = tet_module.run_method(
                    method_name='get',
                    target='%s/%s/details' % (TETRATION_API_APPLICATIONS, application['id'])
                )
                result['object'] = app_details
            else:
                result['object'] = existing_app

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
