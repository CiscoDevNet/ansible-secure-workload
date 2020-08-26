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

version_added: "2.8"

description:
    - "Enables management of Cisco Tetration user accounts."
    - "Enables creation, modification, and deletion of accounts."
    - "Capabilities can be added to the user account, but they cannot be deleted."

options:
    app_scope_id:
        description: ID of the user scope. Omit this parameter or set
            it to an empty string to create a user not limited to one
            scope (most people will want to do this).
            Scope ID and scope name are mutually exclusive.
        type: string
        required: false
    app_scope_name:
        description: Name of the root scope in which to place the user. Omit this parameter
            or set it to an empty string to create a user not limited to one scope. Scope
            ID and scope name are mutually exclusive.
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
    state:
        choices: [present, absent, query]
        description: Add, change, remove or search for the user
        type: string
        required: true

extends_documentation_fragment: tetration_doc_common

author:
    - Your Name (@joej164 and @dchosnek)
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
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        app_scope_id=dict(type='str', required=False, default=''),
        app_scope_name=dict(type='str', required=False, default=''),
        email=dict(type='str', required=True),
        first_name=dict(type='str', required=False, default=''),
        last_name=dict(type='str', required=False, default=''),
        state=dict(type='str', required=True, choices=[
                   'present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        object=None,
        changed=False,
    )

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

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ['app_scope_id', 'app_scope_name']
        ]
    )

    tet_module = TetrationApiModule(module)

    # state = module.params['state']
    # email = module.params['email']
    # first_name = module.params['first_name']
    # last_name = module.params['last_name']
    # app_scope_id = module.params['app_scope_id']
    # app_scope_name = module.params['app_scope_name']

    # The first thing we have to do is get the object.
    returned_object = tet_module.get_object(
        target=TETRATION_API_USER,
        params=dict(include_disabled='true'),
        filter=dict(email=module.params['email']),
    )

    if returned_object:
        result_obj['app_scope_id'] = returned_object['app_scope_id']
        result_obj['created_at'] = returned_object['created_at']
        result_obj['disabled_at'] = returned_object['disabled_at']
        result_obj['email'] = returned_object['email']
        result_obj['first_name'] = returned_object['first_name']
        result_obj['id'] = returned_object['id']
        result_obj['last_name'] = returned_object['last_name']
        result_obj['role_ids'] = returned_object['role_ids']

        result['object'] = result_obj

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # if module.check_mode:
    #     module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if module.params['state'] == 'present':
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['state'] == 'absent':
        module.fail_json(msg='You requested this to fail', **result)

    if module.params['state'] == 'query':
        result['changed'] = False

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
