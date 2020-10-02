ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
author: Brandon Beck (@techbeck03)
description: Enables creation, modification, deletion and query of application policy
  ports
extends_documentation_fragment: tetration
module: tetration_application_policy_ports
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  app_id:
    description: The id for the Application to which the policy belongs
    type: string
  app_scope_id:
    description: The id for the Scope associated with the application
    type: string
  end_port:
    description: End port of the range
    type: int
  policy_id:
    description: Unique identifier for the policy
    required: true
    type: string
  proto_id:
    description: Protocol Integer value (NULL means all protocols)
    type: int
  proto_name:
    description: Protocol name (Ex TCP, UDP, ICMP, ANY)
    type: string
  start_port:
    description: Start port of the range
    type: int
  state:
    choices: '[present, absent, query]'
    description: Add, change, remove or query for application policy ports
    required: true
    type: string
  version:
    description: Indications the version of the Application for which to get the policies
    required: true
    type: string
requirements: tetpyclient
version_added: '2.9'
'''

EXAMPLES = '''
# Add a single port to policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
    version: "v0"
    proto_name: TCP
    start_port: 22
    end_port: 22
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Add ANY port to policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
    version: "v0"
    proto_name: ANY
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete port from policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
    version: "v0"
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  contains:
    id:
      description: Unique identifier for the L4 policy params
      returned: when C(state) is present or query
      sample: 5c93da83497d4f33d7145960
      type: int
    port:
      description: List containing start and end of port range
      returned: when C(state) is present or query
      sample: '[80, 80]'
      type: list
    proto:
      description: Protocol integer ID
      returned: when C(state) is present or query
      sample: 6
      type: string
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATION_POLICIES
from ansible.module_utils.tetration_constants import TETRATION_API_PROTOCOLS
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    valid_proto_names = [proto['name'] for proto in TETRATION_API_PROTOCOLS]
    valid_proto_ids = [proto['value'] for proto in TETRATION_API_PROTOCOLS if isinstance(proto['value'], int)]

    module_args = dict(
        policy_id=dict(type='str', required=True),
        version=dict(type='str', required=True),
        start_port=dict(type='int', required=False),
        end_port=dict(type='int', required=False),
        proto_id=dict(type='int', required=False, choices=valid_proto_ids),
        proto_name=dict(type='str', required=False, choices=valid_proto_names),
        description=dict(type='str', required=False),
        state=dict(required=True, choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ['proto_name', 'proto_id']
        ],
        required_one_of=[
            ['proto_id', 'proto_name'],
        ],
        required_together=[
            ['start_port', 'end_port']
        ],
        required_if=[
            # Only the TCP and UDP protocols require the start and end ports
            ['proto_name', 'TCP', ['start_port', 'end_port']],
            ['proto_name', 'UDP', ['start_port', 'end_port']],
            ['proto_id', 6, ['start_port', 'end_port']],
            ['proto_id', 17, ['start_port', 'end_port']],
        ]
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': None,
    }

    # state = module.params['state']
    # app_id = module.params['app_id']
    # app_scope_id = module.params['app_scope_id']
    # policy_id = module.params['policy_id']
    # version = module.params['version']
    # start_port = module.params['start_port']
    # end_port = module.params['end_port']
    # proto_id = module.params['proto_id']
    # proto_name = module.params['proto_name']
    # existing_app = None
    # existing_app_scope = None
    # existing_policy = None
    # existing_param = None

    # =========================================================================
    # Get current state of the object
    route = f"{TETRATION_API_APPLICATION_POLICIES}/{module.params['policy_id']}"

    existing_policy = tet_module.run_method('GET', route)
    if not existing_policy:
        module.fail_json(msg=f"Unable to find existing application policy with id: {module.params['policy_id']}")

    # Convert the protocol name to a protocol id
    if module.params['proto_name']:
        proto_id_list = [i['value'] for i in TETRATION_API_PROTOCOLS if i['name'] == module.params['proto_name']]
        proto_id = proto_id_list[0]
    else:
        proto_id = module.params['proto_id']

    existing_l4_params = existing_policy['l4_params']

    result['l4_params'] = existing_l4_params

    existing_param = {}
    if existing_l4_params:
        if proto_id == "":
            # The any protocol has a None value
            found_params = [p for p in existing_l4_params if p['proto'] is None]
        elif proto_id in [6, 17]:
            # Find the matching object if the object is a TCP or UDP protocol
            found_params = [p for p in existing_l4_params if p['proto'] == proto_id and p['port']
                            [0] == module.params['start_port'] and p['port'][1] == module.params['end_port']]
        else:
            # Search for anything else
            found_params = [p for p in existing_l4_params if p['proto'] == proto_id]

        if found_params:
            existing_param = found_params[0]

    # =========================================================================
    # Now enforce the desired state (present, absent, query)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':

        # if the object does not exist at all, create it
        new_object = dict(
            version=module.params['version'],
            start_port=module.params['start_port'],
            end_port=module.params['end_port'],
            proto=proto_id if proto_name != 'ANY' else None
        )

        if not existing_param:
            if not module.check_mode:
                param_object = tet_module.run_method(
                    method_name='post',
                    target='%s/%s/l4_params' % (TETRATION_API_APPLICATION_POLICIES, policy_id),
                    req_payload=new_object
                )
                new_object['id'] = param_object['id']
            result['changed'] = True
            result['object'] = param_object
        else:
            result['changed'] = False
            result['object'] = existing_param

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif module.params['state'] == 'absent':
        if existing_param:
            if not module.check_mode:
                tet_module.run_method(
                    method_name='delete',
                    target='%s/%s/l4_params/%s' % (TETRATION_API_APPLICATION_POLICIES, policy_id, existing_param['id'])
                )
            result['changed'] = True

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif module.params['state'] == 'query':
        result['object'] = existing_param

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
