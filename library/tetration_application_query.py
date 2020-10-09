ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_application_query

short_description: Search the application api for scope id's or details

version_added: '2.9'

description:
    - "Search the Application API by a variety of methods to find existing scopes"

options:
    app_id:
        description:
          - Return details of the exact App ID
          - Mutually exclusive with all other search parameters
          - When searching by App ID will not populate the objects search parameter
        required: false
        type: string
    app_name:
        description:
          - Return all applications with this value in its name
          - Mutually exclusive with C(app_id)
        required: false
        type: string
    is_primary:
        description:
          - Return all applications that are either primary or not primary
          - Leave blank to not search on this value
          - Mutually exclusive with C(app_id)
        required: false
        type: boolean
    is_enforcing:
        description:
          - Return all applications that are enforcing
          - Leave blank to not search on this value
          - Mutually exclusive with C(app_id)
        required: false
        type: boolean
    return_details:
        description:
          - When true, returns all details for the matched app scope id
        required: false
        default: false
        type: boolean

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.

requirements:
- requests
- 'Required API Permission(s): app_policy_management'

author:
    - Joe Jacobs(@joej164)
'''

EXAMPLES = '''
# pass in a message and have changed true
- name: Search for all applications
  tetration_application_query:
    provider: "{{ provider_info }}"

- name: Search for an application by Application ID and return all details
  tetration_application_query:
    app_id: 123abc
    return_details: true
    provider: "{{ provider_info }}"

- name: Search for object with a value in the name and that are primary and enforcing
  tetration_application_query:
    app_name: partial
    is_primary: true
    is_enforcing: true
    provider: "{{ provider_info }}"
'''

RETURN = '''
object:
  contains:
    alternate_query_mode:
      description:
      - Indicates if ‘dynamic mode’ is used for the application.
      - In the dynamic mode, an ADM run creates one or more candidate queries for each cluster.
      sample: false
      type: boolean
    app_scope_id:
      description: ID of the scope assigned to the application.
      sample: 5ed69642755f027a324bd922
      type: string
    author:
      description: First and last name of the user who created the application.
      sample: John Doe
      type: string
    created_at:
      description: Unix timestamp of when the application was created.
      sample: 1591121474
      type: int
    description:
      description: User specified description of the application.
      sample: The application description
      type: string
    enforced_version:
      description: The enforced p* version of the application.
      sample: 0
      type: int
    enforcement_enabled:
      description: Indicates if enforcement is enabled on the application
      sample: true
      type: boolean
    id:
      description: A unique identifier for the application.
      sample: 5ed69642755f027a324bd922
      type: string
    latest_adm_version:
      description: The latest adm (v*) version of the application.
      sample: 0
      type: int
    name:
      description: User specified name of the application.
      sample: Application Name
      type: string
    primary:
      description: Indicates if the application is primary for its scope.
      sample: true
      type: boolean
  description: the first object found in the array
  returned: when an item is found
  type: complex
objects:
    description: an array of all objects found
    returned: when an item is found, otherwise is empty, also empty when searching by id
    type: list of object
items_found:
    description: Number of items found when searching
    returned: always
    type: int
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration_constants import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        app_id=dict(type='str', required=False),
        app_name=dict(type='str', required=False),
        is_primary=dict(type='bool', required=False),
        is_enforcing=dict(type='bool', required=False),
        return_details=dict(type='bool', required=False, default=False),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    result = {
        'changed': False,
        'object': {},
        'objects': [],
        'items_found': 0
    }

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ['app_id', 'app_name'],
            ['app_id', 'is_primary'],
            ['app_id', 'is_enforcing'],
        ]
    )

    tet_module = TetrationApiModule(module)
    if module.params['app_id']:
        route = f"{TETRATION_API_APPLICATIONS}/{module.params['app_id']}"
        if module.params['return_details']:
            route = f"{route}/details"
        app_response = tet_module.run_method('GET', route)
        result['object'] = app_response
        if app_response:
            result['items_found'] = 1
    else:
        all_apps_response = tet_module.run_method('GET', TETRATION_API_APPLICATIONS)

        for app in all_apps_response:
            if module.params['app_name'] and module.params['app_name'] not in app['name']:
                continue
            if module.params['is_primary'] is not None and module.params['is_primary'] != app['primary']:
                continue
            if module.params['is_enforcing'] is not None and module.params['is_enforcing'] != app['enforement_enabled']:
                continue

            if module.params['return_details']:
                route = f"{TETRATION_API_APPLICATIONS}/{app['id']}/details"
                details = tet_module.run_method('GET', route)
                result['objects'].append(details)
            else:
                result['objects'].append(app)

        result['items_found'] = len(result['objects'])
        if result['objects']:
            result['object'] = result['objects'][0]

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
