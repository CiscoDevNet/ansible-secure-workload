ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_scope_commit_query_changes

short_description: Commits changes made to short query parameters

version_added: "2.8"

description:
    - "When changes are made to a scopes short query, they are not actually commited"
    - "This modules allows you to commit the changes.  "
    - "Supported options are to do it now or to queue the job"

notes:
    - "If the command successfully runs, always returns as changed even if no short queries need updating"

options:
    root_app_scope_id:
        description:
            - The App Scope ID for which any short queries that need updating will be updated
            - Updates the app scope id listed and any app scope id's under it
        required: true
        type: string
    sync:
        description:
            - Controls whether to run the job immediatly (True) or to queue the job
        required: false
        default: false
        type: bool

extends_documentation_fragment: tetration_doc_common

author:
    - Joe Jacobs (@joej164)
'''

EXAMPLES = '''
# Pass in a message
- name: Commit scope query changes via queuing
  tetration_scope_commit_query_changes:
    root_app_scope_id: abc123
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

- name: Commit scope query changes immediately
  tetration_scope_commit_query_changes:
    root_app_scope_id: abc123
    sync: true
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
success:
    description: Boolean value describing whether the command successfully ran or not 
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        root_app_scope_id=dict(type='str', required=True),
        sync=dict(type='bool', required=False, default=False),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    result = dict(
        changed=False,
        object={},
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    tet_module = TetrationApiModule(module)
    all_scopes_response = tet_module.run_method('GET', TETRATION_API_SCOPES)
    all_scopes_lookup = {s['id']: s['short_name'] for s in all_scopes_response}

    if module.params['root_app_scope_id'] and module.params['root_app_scope_id'] not in all_scopes_lookup.keys():
        error_message = "`root_app_scope_id` passed into the module does not exist."
        module.fail_json(msg=error_message, searched_scope=module.params['root_app_scope_id'])

    req_payload = {
        'root_app_scope_id': module.params['root_app_scope_id'],
        'sync': module.params['sync']
    }

    route = f"{TETRATION_API_SCOPES}/commit_dirty"
    response = tet_module.run_method('POST', route, req_payload=req_payload)

    result['object'] = response
    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
