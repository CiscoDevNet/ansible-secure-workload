#!/usr/bin/python

# MIT License - See LICENSE file in the module


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_user

short_description: Allows for working with user accounts in Tetration

version_added: '2.9'

description:
    - "Enables management of Cisco Tetration user accounts."
    - "Enables creation, modification, and deletion of accounts."
    - "Roles can be added and removed"
    - "Names can be modified"

options:
    app_scope_id:
        description: ID of the user scope. Omit this parameter or set
            it to an empty string to create a user not limited to one
            scope (most people will want to do this).
            C(app_scope_id) and C(app_scope_name) are mutually exclusive.
        type: string
        required: false
    app_scope_name:
        description: Name of the root scope in which to place the user.
            Omit this parameter or set it to an empty string to create
            a user not limited to one scope.
            C(app_scope_id) and C(app_scope_name) are mutually exclusive.
        type: string
        required: false
    email:
        description: User email address (must be unique within Tetration)
        type: string
        required: true
    first_name:
        description: User first name is only required when creating a new user. This parameter
            can optionally be used to change the first name of an existing user.
        type: string
        required: false
    last_name:
        description: User last name is only required when creating a new user. This parameter
            can optionally be used to change the last name of an existing user.
        type: string
        required: false
    role_ids:
        description: List of role ID's that should be applied to the user.
            C(role_ids) and C(role_names) are mutually exclusive.
        type: list
        required: false
        default: []
    role_names:
        description: List of role names that should be applied to the user.
            C(role_ids) and C(role_names) are mutually exclusive.
        type: list
        required: false
        default: []
    state:
        choices: [present, absent, query]
        description: Add, change, remove or search for the user
        type: string
        required: true

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.
- Supports check mode

requirements:
- requests
- 'Required API Permission(s): user_role_scope_management'

author:
    - Doron Chosnek (@dchosnek)
    - Joe Jacobs (@joej164)
'''

EXAMPLES = '''
# Create new user or update first/last name of existing user
- tetration_user:
    provider: "{{ my_tetration }}"
    email: bsmith@example.com
    first_name: Bob
    last_name: Smith
    state: present

# Move user to the specified root scope
- tetration_user:
    provider: "{{ my_tetration }}"
    email: bsmith@example.com
    state: present
    app_scope_name: Default

# Get details for existing user, including what roles are
# assigned to that user
- tetration_user:
    provider: "{{ my_tetration }}"
    email: bsmith@example.com
    state: query

# Disable a user (Tetration users are never really deleted)
- tetration_user:
    provider: "{{ my_tetration }}"
    email: bsmith@example.com
    state: absent

'''

RETURN = '''
object:
    description: Contents of the object in the system
    returned: If exists
    type: complex
    contains:
        app_scope_id:
            description: The scope to which the user is assigned.  Maybe empty if the user is a Service Provider User.
            returned: always
            sample: '""'
            type: string
        created_at:
            description: Unix timestamp of when the user was created.
            returned: always
            sample: '1541993885.0'
            type: int
        disabled_at:
            description: Unix timestamp of when the user has been disabled.
                Zero or null otherwise.
            returned: always
            sample: 'null'
            type: int
        email:
            description: Email associated with user account.
            returned: always
            sample: bsmith@example.com
            type: string
        first_name:
            description: First name.
            returned: always
            sample: Bob
            type: string
        id:
            description: Unique identifier for the user role.
            returned: always
            sample: 5bb7eaa3497d4f4e657ca65a
            type: string
        last_name:
            description: Last name.
            returned: always
            sample: Smith
            type: string
        role_ids:
            description: List of IDs of roles assigned to the user account.
            returned: always
            sample: ["5bb7bc06497d4f231c3bd481", "5bb7bc06497d4f231c3bd481"]
            type: list
        '''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_USER
from ansible.module_utils.tetration_constants import TETRATION_API_ROLE
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        app_scope_id=dict(type='str', required=False, default=''),
        app_scope_name=dict(type='str', required=False, default=''),
        role_ids=dict(type='list', required=False, default=[]),
        role_names=dict(type='list', required=False, default=[]),
        email=dict(type='str', required=True),
        first_name=dict(type='str', required=False, default=''),
        last_name=dict(type='str', required=False, default=''),
        state=dict(type='str', required=True, choices=[
                   'present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # Create the objects that will be returned
    result = {
        "object": None,
        "changed": False,
    }

    result_obj = dict(
        app_scope_id=None,
        created_at=None,
        disabled_at=None,
        email=None,
        first_name=None,
        id=None,
        last_name=None,
        role_ids=[]
    )

    # Creating the Ansible Module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ['app_scope_id', 'app_scope_name'],
            ['role_ids', 'role_names']
        ]
    )

    tet_module = TetrationApiModule(module)

    # Create an App Scope Name to ID Lookup Table
    all_app_scopes_response = tet_module.run_method('GET', TETRATION_API_SCOPES)
    all_app_scopes_lookup = {r['name']: r['id'] for r in all_app_scopes_response}

    # Create a Role Name to ID Lookup Table
    all_roles_response = tet_module.run_method('GET', TETRATION_API_ROLE)
    all_roles_lookup = {r['name']: r['id'] for r in all_roles_response}

    # Role and App Scope Validation
    # Done here so it does not have to be done elsewhere in the module
    invalid_parameters = {}
    if module.params['app_scope_id']:
        scope_id = module.params['app_scope_id']
        if scope_id not in all_app_scopes_lookup.values():
            invalid_parameters['app_scope_id'] = scope_id
    if module.params['app_scope_name']:
        scope_name = module.params['app_scope_name']
        if scope_name not in all_app_scopes_lookup.keys():
            invalid_parameters['app_scope_name'] = scope_name
    if module.params['role_ids']:
        invalid_role_ids = [id for id in module.params['role_ids'] if id not in all_roles_lookup.values()]
        if invalid_role_ids:
            invalid_parameters['role_ids'] = invalid_role_ids
    if module.params['role_names']:
        invalid_role_names = [name for name in module.params['role_names'] if name not in all_roles_lookup.keys()]
        if invalid_role_names:
            invalid_parameters['role_names'] = invalid_role_names

    if invalid_parameters:
        error_message = "Check the `invalid parameters` object for the invalid parameters"
        module.fail_json(msg=error_message, invalid_parameters=invalid_parameters)

    # The first thing we have to do is get the object.
    returned_user_object = tet_module.get_object(
        target=TETRATION_API_USER,
        params=dict(include_disabled='true'),
        filter=dict(email=module.params['email']),
    )

    if returned_user_object:
        user_id = returned_user_object['id']
    else:
        user_id = None

    # Create the user, update the user, or verify no changes needed
    if module.params['state'] == 'present':
        if returned_user_object is None:
            # User does not exist, so we're going to create it
            req_payload = {
                "first_name": "",
                "last_name": "",
                "email": "",
                "app_scope_id": "",
                "role_ids": []
            }

            # Check for required parameters when creating a user
            if not all([module.params['first_name'], module.params['last_name']]):
                error_message = (
                    'The first name and last name parameters are required when '
                    'creating a new user.  '
                    'First Name: {} '
                    'Last Name: {}').format(module.params['first_name'], module.params['last_name'])
                module.fail_json(msg=error_message)

            # Now that we know the required parameters exist, update the request object
            req_payload['first_name'] = module.params['first_name']
            req_payload['last_name'] = module.params['last_name']
            req_payload['email'] = module.params['email']

            # Deal with the `app_scope` parameters
            if module.params['app_scope_name']:
                # Convert the name to a scope id
                app_scope_id = all_app_scopes_lookup.get(module.params['app_scope_name'])
                req_payload['app_scope_id'] = app_scope_id

            elif module.params['app_scope_id']:
                req_payload['app_scope_id'] = module.params['app_scope_id']
            else:
                # No data was provided, remove the parameter
                req_payload.pop('app_scope_id')

            # Deal with the `role` parameters
            if module.params['role_names']:
                # Convert the list of names to a list of id's
                for role_name in module.params['role_names']:
                    role_id = all_roles_lookup.get(role_name)
                    req_payload['role_ids'].append(role_id)

            elif module.params['role_ids']:
                req_payload['role_ids'] = module.params['role_ids']
            else:
                # No data was provided, remove the parameter
                req_payload.pop('role_ids')

            if module.check_mode:
                # We just document what we would have changed
                result['changed'] = True
                for k in result_obj.keys():
                    result_obj[k] = req_payload.get(k)
            else:
                method_results = tet_module.run_method('POST', TETRATION_API_USER, req_payload=req_payload)
                if method_results:
                    result['changed'] = True
                    for k in result_obj.keys():
                        result_obj[k] = method_results.get(k)

        elif returned_user_object is not None:

            if returned_user_object['disabled_at']:
                # Re-enable the user if it's disabled
                enable_route = f'{TETRATION_API_USER}/{user_id}/enable'
                if not module.check_mode:
                    method_results = tet_module.run_method('POST', enable_route)
                    result_obj['disabled_at'] = method_results['disabled_at']
                else:
                    result_obj['disabled_at'] = None
                result['changed'] = True

            req_payload = {
                "first_name": "",
                "last_name": "",
                "email": "",
                "app_scope_id": ""
            }

            # Set the request payload object to update the user
            if module.params['first_name'] and returned_user_object['first_name'] != module.params['first_name']:
                req_payload['first_name'] = module.params['first_name']
                result_obj['first_name'] = module.params['first_name']
                result['changed'] = True
            else:
                result_obj['first_name'] = returned_user_object['first_name']
                req_payload.pop('first_name')

            if module.params['last_name'] and returned_user_object['last_name'] != module.params['last_name']:
                req_payload['last_name'] = module.params['last_name']
                result_obj['last_name'] = module.params['last_name']
                result['changed'] = True
            else:
                result_obj['last_name'] = returned_user_object['last_name']
                req_payload.pop('last_name')

            if module.params['email'] and returned_user_object['email'] != module.params['email']:
                req_payload['email'] = module.params['email']
                result_obj['email'] = module.params['email']
                result['changed'] = True
            else:
                result_obj['email'] = returned_user_object['email']
                req_payload.pop('email')

            if module.params['app_scope_id']:
                if returned_user_object['app_scope_id'] != module.params['app_scope_id']:
                    req_payload['app_scope_id'] = module.params['app_scope_id']
                    result_obj['app_scope_id'] = module.params['app_scope_id']
                    result['changed'] = True
                else:
                    result_obj['app_scope_id'] = returned_user_object['app_scope_id']
                    req_payload.pop('app_scope_id')
            elif module.params['app_scope_name']:
                app_scope_id = all_app_scopes_lookup.get(module.params['app_scope_name'])
                if returned_user_object['app_scope_id'] != app_scope_id:
                    req_payload['app_scope_id'] = app_scope_id
                    result_obj['app_scope_id'] = app_scope_id
                    result['changed'] = True
                else:
                    result_obj['app_scope_id'] = returned_user_object['app_scope_id']
                    req_payload.pop('app_scope_id')
            else:
                result_obj['app_scope_id'] = returned_user_object['app_scope_id']
                req_payload.pop('app_scope_id')

            update_route = f'{TETRATION_API_USER}/{user_id}'
            if not module.check_mode:
                method_results = tet_module.run_method('PUT', update_route, req_payload=req_payload)

            roles_to_add = []
            roles_to_delete = []

            if module.params['role_ids']:
                current_state = set(returned_user_object['role_ids'])
                desired_state = set(module.params['role_ids'])

                roles_to_add = list(desired_state.difference(current_state))
                roles_to_delete = list(current_state.difference(desired_state))

            elif module.params['role_names']:
                current_state = set(returned_user_object['role_ids'])
                desired_state = []
                for name in module.params['role_names']:
                    desired_state.append(all_roles_lookup[name])
                desired_state = set(desired_state)

                roles_to_add = list(desired_state.difference(current_state))
                roles_to_delete = list(current_state.difference(desired_state))

            # Set the results equal to what it is currently
            result_obj['role_ids'] = returned_user_object['role_ids']

            req_payload = {
                "role_id": None,
            }
            for role in roles_to_add:
                add_role_route = f"{TETRATION_API_USER}/{user_id}/add_role"
                req_payload['role_id'] = role
                result_obj['role_ids'].append(role)
                if not module.check_mode:
                    method_results = tet_module.run_method('PUT', add_role_route, req_payload=req_payload)
                result['changed'] = True
            for role in roles_to_delete:
                req_payload['role_id'] = role
                result_obj['role_ids'] = [r for r in result_obj['role_ids'] if r != role]
                remove_role_route = f"{TETRATION_API_USER}/{user_id}/remove_role"
                if not module.check_mode:
                    method_results = tet_module.run_method('DELETE', remove_role_route, req_payload=req_payload)
                result['changed'] = True

    if module.params['state'] == 'absent':
        if returned_user_object and not returned_user_object['disabled_at']:
            # If the user exists and it's not already disabled, a change will occur
            result['changed'] = True

            if not module.check_mode:
                route = f"{TETRATION_API_USER}/{user_id}"
                method_results = tet_module.run_method('DELETE', route)
                if method_results:
                    for k in result_obj.keys():
                        result_obj[k] = method_results.get(k)
            else:
                # Extracting the reqired info from what was returned from Tetration
                result_obj['app_scope_id'] = returned_user_object['app_scope_id']
                result_obj['created_at'] = returned_user_object['created_at']
                result_obj['disabled_at'] = returned_user_object['disabled_at']
                result_obj['email'] = returned_user_object['email']
                result_obj['first_name'] = returned_user_object['first_name']
                result_obj['id'] = returned_user_object['id']
                result_obj['last_name'] = returned_user_object['last_name']
                result_obj['role_ids'] = returned_user_object['role_ids']

    if module.params['state'] == 'query':
        result['changed'] = False
        if returned_user_object is not None:
            # Extracting the reqired info from what was returned from Tetration
            result_obj['app_scope_id'] = returned_user_object['app_scope_id']
            result_obj['created_at'] = returned_user_object['created_at']
            result_obj['disabled_at'] = returned_user_object['disabled_at']
            result_obj['email'] = returned_user_object['email']
            result_obj['first_name'] = returned_user_object['first_name']
            result_obj['id'] = returned_user_object['id']
            result_obj['last_name'] = returned_user_object['last_name']
            result_obj['role_ids'] = returned_user_object['role_ids']

    result['object'] = result_obj
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
