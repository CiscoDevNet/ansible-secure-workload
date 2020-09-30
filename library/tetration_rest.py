#!/usr/bin/python
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: tetration_rest

short_description: Direct access to the Tetration API (non-idempotent)

version_added: '2.9'

description:
- Enables management of Cisco Tetration through direct access to the Cisco Tetration
  REST API.
- The Cisco Tetration API is not idempotent, so this module is not idempotent.
- Familiarity with the Cisco Tetration API is required to use this module. Documentation
  for the API is available at the Cisco Tetration web UI.

options:
  method:
    choices: [delete, get, post, put]
    description: REST method
    required: true
    type: string
  route:
    description: API endpoint such as 'roles' or 'users'
    required: true
    type: string
  params:
    description: parameters for REST call is used if I(method=get)
    type: dict
  payload:
    description: payload for REST call is used if I(method=put) or I(method=post)
    type: dict

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.
- This module is not idempotent.
- Does not support check mode.

requirements: 
- requests 

author:
    - Doron Chosnek (@dchosnek)
    - Joe Jacobs (@joej164)
'''

EXAMPLES = '''
# Query existing users.
- tetration_rest:
    provider: "{{ my_tetration }}"
    route: users
    method: get
    params:
      include_disabled: true

# Create an inventory filter. Running this more than once will return a
# status code of 422 because the filter cannot be created twice.
- tetration_rest:
    provider: "{{ my_tetration }}"
    route: filters/inventories
    method: post
    payload:
      name: my new filter
      query:
        type: eq
        field: ip
        value: 172.16.200.100
      app_scope_id: 5bb7bc01497d4f228d6b8123

# Update the description for an existing role. Running this more than once
# will succeed but will also report changed=true even though changes have
# not been made.
- tetration_rest:
    provider: "{{ my_tetration }}"
    route: roles/5bbe916e497d4f0af77ca6c8
    method: put
    payload:
      description: updated role description

# Delete one software agent.
- tetration_rest:
    provider: "{{ my_tetration }}"
    route: sensors/3e2bbb8066908f83b61eb000044e8abb5f3e79bf
    method: delete
'''

RETURN = '''
---
object:
  contains:
    json:
      description: JSON response document from REST method
      returned: success
      type: dict
    ok:
      description: Indicates if operation was successful
      returned: always
      sample: 'True'
      type: bool
    reason:
      description: Text explanation of the status code
      returned: always
      sample: Not Found
      type: string
    status_code:
      description: HTTP status code for REST method
      returned: always
      sample: 200
      type: int
    text:
      description: Text returned from REST method
      returned: failed
      type: string
  description: The results of the command
  returned: always
  type: complex
'''
import json

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration_constants import TETRATION_API_SUCCESS_CODES
from ansible.module_utils.tetration import RestClient


def main():
    module = AnsibleModule(
        argument_spec=dict(
            route=dict(type='str', required=True),
            method=dict(type='str', required=True, choices=['delete', 'get', 'post', 'put']),
            payload=dict(type='dict', required=False),
            params=dict(type='dict', required=False),
            provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
        ),
        # we can't predict if the proposed API call will make a change to the system
        supports_check_mode=False
    )

    method = module.params['method']
    api_route = '/openapi/' + \
        module.params['provider']['api_version'] + '/' + module.params['route']
    req_payload = module.params['payload']

    restclient = RestClient(
        module.params['provider']['server_endpoint'],
        api_key=module.params['provider']['api_key'],
        api_secret=module.params['provider']['api_secret'],
        verify=module.params['provider']['verify'],
        max_retries=module.params['provider']['max_retries']
    )

    # Do our best to provide "changed" status accurately, but it's not possible
    # as different Tetration APIs react differently to operations like creating
    # an element that already exists.
    changed = False
    if method == 'get':
        response = restclient.get(api_route, params=module.params['params'])
    elif method == 'delete':
        response = restclient.delete(api_route)
        changed = True if response.status_code in TETRATION_API_SUCCESS_CODES else False
    elif method == 'post':
        response = restclient.post(api_route, json_body=json.dumps(req_payload))
        changed = True if response.status_code in TETRATION_API_SUCCESS_CODES else False
    elif method == 'put':
        response = restclient.put(api_route, json_body=json.dumps(req_payload))
        changed = True if response.status_code in TETRATION_API_SUCCESS_CODES else False
    else:
        response = None
        module.fail_json(msg='Unsupported HTTP Verb, only supported Methods are get, delete, post, and put')

    # Put status_code in the return JSON. If the status_code is not 200, we
    # add the text that came from the REST call and the payload to make
    # debugging easier.
    result = {}
    result['status_code'] = response.status_code
    result['ok'] = response.ok
    result['reason'] = response.reason
    if response.status_code in TETRATION_API_SUCCESS_CODES:
        result['json'] = response.json()
    else:
        result['text'] = response.text

    module.exit_json(changed=changed, **result)


if __name__ == '__main__':
    main()
