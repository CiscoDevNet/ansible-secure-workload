#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_role

short_description: Manage roles and capabilities

version_added: '2.8'

description:
- Enables management of Cisco Tetration roles.
- Enables creation, modification, and deletion of roles.
- Can add capabilities to a role, but cannot modify or delete capabilities.

notes:
- Supports check mode.

options:
  app_scope_id:
    default: '""'
    description: ID of the scope where the role exists. An empty string means it is
      a service provider role.
    type: string
  capability_ability:
    choices: [SCOPE_READ, SCOPE_WRITE, EXECUTE, ENFORCE, SCOPE_OWNER, DEVELOPER]
    description: The name of the ability assigned to a role. Multiple abilities can
      be assigned to a role with a loop. Abilities can be added but cannot be removed
      from a role. Capability_appscope and capability_ability are not required parameters
      but must be specified together.
    type: string
  capability_app_scope_id:
    description: ID of the app scope in which the capability has abilities
    type: string
  description:
    description: description of the role
    type: string
  id:
    description: GUID for the role to be altered or deleted. Must specify either id
      or name and app_scope_id.  If both C(name) and C(id) are specified, C(id) will be preferred.
    type: string
  name:
    description: Name of the role. Must specify either id or name and app_scope_id.
      If both C(name) and C(id) are specified, C(id) will be preferred.
    type: string
  state:
    choices: [present, absent, query]
    description: Add, change, remove or search for the role
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

author:
    - Doron Chosnek (@dchosnek)
    - Joe Jacobs (@joej164)
'''

EXAMPLES = '''
  # Query an existing role by name (query can be done by name or ID)
  - tetration_role:
      provider: "{{ my_tetration }}"
      name: expenses app owner
      state: query

  # Create or modify an existing role that has read access to the specified scope.
  # You can create a role with no capabilities, but that would not be useful.
  - tetration_role:
      provider: "{{ my_tetration }}"
      name: expenses app reader
      description: read only access to the expenses application
      state: present
      capability_ability: read
      capability_appscope: "{{ expenses_app_scope }}"

  # Set description of a role (name can also be changed when you specify the ID of the role)
  - tetration_role:
      provider: "{{ my_tetration }}"
      id: "{{ expenses_reader.object.id }}"
      description: modified name and desc for app reader
      state: present

  # All of the above examples can be done to roles inside an app scope
  # by specifying the app_scope_id variable
  - tetration_role:
      provider: "{{ my_tetration }}"
      name: app reader subscope
      description: role in a subscope
      app_scope_id: "{{ default_scope }}"
      state: present

  # Add multiple capabilities to a role using loop
  - tetration_role:
      provider: "{{ my_tetration }}"
      name: expenses app owner
      state: present
      capability_ability: "{{ item.ability }}"
      capability_appscope: "{{ item.scope }}"
    loop:
    - { scope: "{{ expenses_app_scope }}", ability: 'execute' }
    - { scope: "{{ expenses_app_scope }}", ability: 'developer' }

  # Delete a role by name
  - tetration_role:
      provider: "{{ my_tetration }}"
      name: expenses app owner
      state: absent
'''

RETURN = '''
---
object:
    description: Contents of the object in the system
    returned: If exists
    type: complex
    contains:
        app_scope_id:
            description: Scope to which the scope is defined, maybe empty for Service Provider Roles.
            returned: when C(state) is present or query
            sample: ''
            type: string
        capabilities:
            description: List of capabilities. Each capability specifies ability, app_scope_id, id, inherited, and role_id.
            returned: when C(state) is present or query and the role has capabilities
            type: list
        description:
            description: User specified description for the role.
            returned: when C(state) is present or query
            sample: allows for reading of the expenses application
            type: string
        id:
            description: Unique identifier for the role.
            returned: when C(state) is present or query
            sample: 5bc0bb14497d4f143b7ca660
            type: string
        name:
            description: User specified name for the role.
            returned: when C(state) is present or query
            sample: Expenses App Reader
            type: string
'''


from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_ROLE
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration_constants import TETRATION_API_APP_SCOPE_CAPABILITIES
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    module_args = dict(
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        app_scope_id=dict(type='str', required=False),
        id=dict(type='str', required=False),
        capability_app_scope_id=dict(type='str', required=False),
        capability_ability=dict(type='str', required=False, choices=TETRATION_API_APP_SCOPE_CAPABILITIES),
        state=dict(type='str', required=True, choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # Create the objects that will be returned
    result = {
        "object": None,
        "changed": False
    }

    result_obj = dict(
        app_scope_id=None,
        capabilities=[],
        description=None,
        id=None,
        name=None
    )

    # Creating the Ansible Module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_one_of=[
            ['id', 'name']
        ],
        required_together=[
            ['capability_app_scope_id', 'capability_ability']
        ],
        required_by={
            'name': ['app_scope_id']
        }
    )

    # grant capablities (present)
    # role_id, capability app scope id, ability

    tet_module = TetrationApiModule(module)

    # Create an App Scope Name to ID Lookup Table
    all_app_scopes_response = tet_module.run_method('GET', TETRATION_API_SCOPES)
    all_app_scopes_lookup = {r['name']: r['id'] for r in all_app_scopes_response}

    # Create a Role Name - App Scope ID to Role ID Lookup Table
    # A role is uniquely identified by its name and app scope
    all_roles_response = tet_module.run_method('GET', TETRATION_API_ROLE)
    all_roles_lookup_by_name_app_id = {f"{r['name']}-{r['app_scope_id']}": r['id'] for r in all_roles_response}

    # Role and App Scope Validation
    # Done here so it does not have to be done elsewhere in the module
    invalid_parameters = {}
    if module.params['app_scope_id']:
        scope_id = module.params['app_scope_id']
        if scope_id not in all_app_scopes_lookup.values():
            invalid_parameters['app_scope_id'] = scope_id
    if module.params['id']:
        role_id = module.params['id']
        if role_id not in all_roles_lookup_by_name_app_id.values():
            invalid_parameters['id'] = role_id

    if invalid_parameters:
        error_message = "Check the `invalid parameters` object for the invalid parameters"
        module.fail_json(msg=error_message, invalid_parameters=invalid_parameters)

    # One of these is the unique ID for the role
    role_id = module.params['id']
    name_scope_id = f"{module.params['name']}-{module.params['app_scope_id']}"

    if module.params['state'] == 'present':
        if not role_id and name_scope_id not in all_roles_lookup_by_name_app_id.keys():
            # Role does not exist, lets add it
            req_payload = {
                'name': module.params['name'],
                'description': module.params['description'],
                'app_scope_id': module.params['app_scope_id']
            }
            response = tet_module.run_method('POST', TETRATION_API_ROLE, req_payload=req_payload)
            result_obj = response
            result['changed'] = True
        else:
            # The Role exists, lets update it
            if role_id:
                route = f'{TETRATION_API_ROLE}/{role_id}'
            else:
                looked_up_role_id = all_roles_lookup_by_name_app_id[name_scope_id]
                route = f'{TETRATION_API_ROLE}/{looked_up_role_id}'

            response = tet_module.run_method('GET', route)

            req_payload = {
                'name': module.params['name'],
                'description': module.params['description'],
            }

            if module.params['name'] is None or module.params['name'] == response['name']:
                req_payload.pop('name', None)

            if module.params['name'] is None or module.params['description'] == response['description']:
                req_payload.pop('description')

            if req_payload:
                updated_response = tet_module.run_method('PUT', route, req_payload=req_payload)
                result['changed'] = True
                result_obj = updated_response
            else:
                result_obj = response

        if module.params['capability_app_scope_id']:
            # Check to see if any capabilities can be added
            pass

    if module.params['state'] == 'absent':
        if module.params['id'] and module.params['name']:
            error_message = (
                'Cannot search for 2 parameters at the same time, specify either `name` or `id`'
            )
            module.fail_json(msg=error_message)

        if not role_id and name_scope_id not in all_roles_lookup_by_name_app_id.keys():
            module.exit_json(msg='That role does not exist in the system.', object={'success': True})

        if role_id:
            route = f'{TETRATION_API_ROLE}/{role_id}'
        else:
            looked_up_role_id = all_roles_lookup_by_name_app_id[name_scope_id]
            route = f'{TETRATION_API_ROLE}/{looked_up_role_id}'

        role_response = tet_module.run_method('DELETE', route)
        result_obj = role_response
        result['changed'] = True

    if module.params['state'] == 'query':
        # Confirm the user didn't try and search for 2 different values
        if module.params['id'] and module.params['name']:
            error_message = (
                'Cannot search for 2 parameters at the same time, specify either `name` or `id`'
            )
            module.fail_json(msg=error_message)

        # Confirm the role exists if searching by name and App Scope ID
        if not role_id and name_scope_id not in all_roles_lookup_by_name_app_id.keys():
            error_message = (
                'There is no role that matches the value being searched for'
            )
            module.fail_json(msg=error_message)

        if role_id:
            route = f'{TETRATION_API_ROLE}/{role_id}'
        else:
            looked_up_role_id = all_roles_lookup_by_name_app_id[name_scope_id]
            route = f'{TETRATION_API_ROLE}/{looked_up_role_id}'

        role_response = tet_module.run_method('GET', route)
        result_obj = role_response

    result['object'] = result_obj
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
