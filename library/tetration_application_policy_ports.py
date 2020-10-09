ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: tetration_application_policy_ports

short description: Enables creation, partial modification, and deletion and query of application policy ports

version_added: '2.9'

description:
- Enables creation, modification, deletion and query of application policy ports

options:
  approved:
    description: approval status of the port
    type: bool
    required: false
  exclusion_filter:
    description: upon deletion of a port entry, controls whether to create an exclusion filter
    type: bool
    required: false
    default: false
  description:
    description: User defined description of the entry
    type: string
    required: false
  end_port:
    description:
    - End port of the range
    - Used only when the C(proto_name) is TCP or UDP or C(proto_id) is 6 or 17
    type: int
  policy_id:
    description: Unique identifier for the policy this port is to be applied to
    type: string
    required: true
  proto_id:
    description:
    - Protocol Integer value.
    - For all protocols us C(proto_name) with the value of `ANY`
    type: int
  proto_name:
    description: Protocol name (Ex TCP, UDP, ICMP, ANY)
    type: string
  start_port:
    description:
    - Start port of the range
    - Used only when the C(proto_name) is TCP or UDP or C(proto_id) is 6 or 17
    type: int
  state:
    choices: [present, absent, query]
    description: Add, change, remove or query for application policy ports
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.
- You cannot update an existing policy port, due to the API, you have to delete a current one and add a new one.
- This also applies to the description, to update the description, you must delete a port and add new one
- The only thing you can update is whether the ports are approved or not using the C(exclusion_filter) parameter
- You cannot specify the `ANY` protocol by C(proto_id), only by C(proto_name)

requirements:
- requests
- 'Required API Permission(s): app_policy_management'

author:
- Brandon Beck (@techbeck03)
- Joe Jacobs (@joej164)
'''

EXAMPLES = '''
# Add a single port to policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
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
    approved:
      description: Whether the port is approved or not
      returned: when port is approved.  absent if not approved
      sample: true
      type: bool
    description:
      description: User entered description of the port
      returned: when a value is entered.  absent if not approved
      sample: true
      type: bool
    id:
      description: Unique identifier for the L4 policy params
      returned: when C(state) is present or query
      sample: 5c93da83497d4f33d7145960
      type: int
    port:
      description: List containing start and end of port range
      returned: when C(state) is present or query and port ID is 6 or 17 for TCP and UDP resepectively
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
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATION_POLICIES
from ansible.module_utils.tetration_constants import TETRATION_API_PROTOCOLS
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def find_l4_param(existing_l4_params=None, proto_id=None, start_port=None, end_port=None):
    found_params = []
    if existing_l4_params is None:
        existing_l4_params = []

    if proto_id is None:
        found_params = [p for p in existing_l4_params if p['proto'] is None]
    elif proto_id in [6, 17]:
        # Find the matching object if the object is a TCP or UDP protocol
        found_params = [p for p in existing_l4_params if p['proto'] ==
                        proto_id and p['port'][0] == start_port and p['port'][1] == end_port]
    else:
        # Search for anything else
        found_params = [p for p in existing_l4_params if p['proto'] == proto_id]

    if found_params:
        return found_params[0]
    else:
        return {}


def main():
    valid_proto_names = [proto['name'] for proto in TETRATION_API_PROTOCOLS]
    valid_proto_ids = [proto['value'] for proto in TETRATION_API_PROTOCOLS]

    module_args = dict(
        policy_id=dict(type='str', required=True),
        start_port=dict(type='int', required=False),
        end_port=dict(type='int', required=False),
        proto_id=dict(type='int', required=False, choices=valid_proto_ids),
        proto_name=dict(type='str', required=False, choices=valid_proto_names),
        description=dict(type='str', required=False),
        approved=dict(type='bool', required=False),
        exclusion_filter=dict(type='bool', required=False, default=False),
        state=dict(required=True, choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ['proto_name', 'proto_id']
        ],
        required_one_of=[
            ['proto_name', 'proto_id'],
        ],
        required_together=[
            ['start_port', 'end_port']
        ],
        required_if=[
            # Only the TCP and UDP protocols require the start and end ports
            ['proto_name', 'TCP', ['start_port', 'end_port']],
            ['proto_name', 'UDP', ['start_port', 'end_port']],
            ['proto_id', 6, ['start_port', 'end_port']],
            ['proto_id', 17, ['start_port', 'end_port']]
        ]
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': {},
    }

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

    existing_param = find_l4_param(existing_l4_params, proto_id, module.params['start_port'], module.params['end_port'])

    # =========================================================================
    # Now enforce the desired state (present, absent, query)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':

        # if the object does not exist at all, create it
        # deal with approved or not approved a different way
        new_object = {
            "start_port": module.params['start_port'],
            "end_port": module.params['end_port'],
            "description": module.params['description'],
            "proto": proto_id
        }

        # Remove unneeded entries
        parameters = [
            'start_port',
            'end_port',
            'description',
        ]

        for p in parameters:
            if new_object[p] is None:
                new_object.pop(p)

        # If the object does not exist, let's create it
        route = f"{TETRATION_API_APPLICATION_POLICIES}/{module.params['policy_id']}/l4_params"

        if not existing_param:
            l4_results = tet_module.run_method('POST', route, req_payload=new_object)

            new_param = find_l4_param(l4_results['l4_params'],
                                      proto_id,
                                      module.params['start_port'],
                                      module.params['end_port'])

            result['object'] = new_param
            result['changed'] = True
        else:
            result['object'] = existing_param

        if module.params['approved'] is not None:
            # If the approval status is missing, that means it's not approved
            current_approval_status = result['object'].get('approved', False)
            current_id = result['object']['id']

            if current_approval_status != module.params['approved']:
                updated_route = f"{route}/{current_id}"

                payload = {
                    "approved": module.params['approved']
                }

                approval_results = tet_module.run_method('PUT', updated_route, req_payload=payload)

                updated_param = find_l4_param(approval_results['l4_params'],
                                              proto_id,
                                              module.params['start_port'],
                                              module.params['end_port'])

                result['object'] = updated_param
                result['changed'] = True
                # ---------------------------------
                # STATE == 'absent'
                # ---------------------------------

    elif module.params['state'] == 'absent':
        if existing_param:
            policy_id = module.params['policy_id']
            l4_param_id = existing_param['id']
            route = f"{TETRATION_API_APPLICATION_POLICIES}/{policy_id}/l4_params/{l4_param_id}"

            payload = {
                "create_exclusion_filter": module.params['exclusion_filter']
            }

            delete_results = tet_module.run_method('DELETE', route, req_payload=payload)

            result['changed'] = True
            result['object'] = delete_results

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif module.params['state'] == 'query':
        result['object'] = existing_param

    # Return result
    module.exit_json(**result)


if __name__ == '__main__':
    main()
