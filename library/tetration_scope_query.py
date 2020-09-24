ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_scope_query 

short_description: Search the scope api for scope id's or details

version_added: "2.8"

description:
    - "Search the Scope API by a variety of methods to find existing scopes"

options:
    fully_qualified_name:
        description:
            - The fully qualified name of the scope you are searching for
            - Looks for an exact match and returns the one found
            - Mutually exclusive with [C(scope_id), C(short_name)]
        required: false
        type: string
    scope_id:
        description:
            - The scope id of the scope you are searching for
            - Looks for an exact match and returns the one found
            - Mutually exclusive with [C(fully_qualified_name), C(short_name)]
        required: false
        type: string
    short_name:
        description:
            - The short name of the scope you are looking for.
            - Looks through all the scopes and looks for short names that contain the value in short_name.
            - Will do partial and exact matches.
            - Mutually exclusive with [C(fully_qualified_name), C(scope_id)]
        required: false
        type: string
    only_dirty:
        description:
            - Filter out non dirty objects if set to true
            - If set to false will return all matches
        type: bool
        default: False


extends_documentation_fragment: tetration_doc_common

author:
    - Your Name (@joej164)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_test:
    name: hello world

# pass in a message and have changed true
- name: Search for dirty scope objects by scope name
  tetration_scope_query:
    short_name: Ignwpov 
    only_dirty: true
    provider: "{{ provider_info }}"

- name: Search for objects by id
  tetration_scope_query:
    scope_id: 123abc
    provider: "{{ provider_info }}"

- name: Search for objects by fully qualified name
  tetration_scope_query:
    fully_qualified_name: RootScopeName:SubScopeName 
    provider: "{{ provider_info }}"
'''

RETURN = '''
object:
  contains:
    child_app_scope_ids:
      description: "An array of child scope ids"
      sample: '[]'
      type: list
    description:
      description: User specified description of the scope
      sample: Scope for ACME example application
      type: string
    dirty:
      description: Indicates a child or parent query has been updated and that the
        changes need to be committed
      sample: 'false'
      type: bool
    dirty_short_query:
      description: Non-null if the query for this scope has been updated but not yet
        committed
      sample: 'null'
      type: dict
    id:
      description: Unique identifier for the scope
      sample: 5c93da83497d4f33d7145960
      type: int
    name:
      description: Fully qualified name of the scope. This is a fully qualified name,
        i.e. it has name of parent scopes (if applicable) all the way to the root
        scope
      sample: ACME:Example:Application
      type: string
    parent_app_scope_id:
      description: ID of the parent scope
      sample: 596d5215497d4f3eaef1fd04
      type: string
    policy_priority:
      description: Used to sort application priorities
      sample: 2
      type: int
    query:
      description: Filter (or match criteria) associated with the scope in conjunction
        with the filters of the parent scopes (all the way to the root scope)
      sample: JSON Filter (full)
      type: dict
    root_app_scope_id:
      description: ID of the root scope this scope belongs to
      sample: 596d3d2f497d4f35380b68ef
      type: string
    short_name:
      description: User specified name of the scope
      sample: Application
      type: string
    short_query:
      description: Filter (or match criteria) associated with the scope
      sample: JSON Filter (short)
      type: dict
    updated_at:
      description: Date this scope was last updated (Unix Epoch)
      sample: 1500402190
      type: int
    vrf_id:
      description: ID of the VRF to which scope belongs to
      sample: 1
      type: int
  description: the first object found
  returned: when an item is found 
  type: complex
objects:
    description: an array of all objects found
    returned: when an item is found, otherwise is empty
    type: list of object
qty_found:
    description: Number of items found when searching
    returned: always
    type: int
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        fully_qualified_name=dict(type='str', required=False),
        scope_id=dict(type='str', required=False),
        short_name=dict(type='str', required=False),
        only_dirty=dict(type='bool', required=False, default=False),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    result = dict(
        changed=False,
        object={},
        objects=[],
        qty_found=0
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['fully_qualified_name', 'scope_id', 'short_name'],
        ],
        mutually_exclusive=[
            ['fully_qualified_name', 'scope_id', 'short_name'],
        ]
    )

    tet_module = TetrationApiModule(module)
    all_scopes_response = tet_module.run_method('GET', TETRATION_API_SCOPES)

    if module.params['fully_qualified_name']:
        to_find = module.params['fully_qualified_name']
        found_scopes = [s for s in all_scopes_response if s['name'] == to_find]
        if module.params['only_dirty']:
            found_scopes = [s for s in found_scopes if s['dirty'] == True]
        result['objects'] = found_scopes
        result['qty_found'] = len(found_scopes)
        if found_scopes:
            result['object'] = found_scopes[0]
    elif module.params['scope_id']:
        to_find = module.params['scope_id']
        found_scopes = [s for s in all_scopes_response if s['id'] == to_find]
        if module.params['only_dirty']:
            found_scopes = [s for s in found_scopes if s['dirty'] == True]
        result['objects'] = found_scopes
        result['qty_found'] = len(found_scopes)
        if found_scopes:
            result['object'] = found_scopes[0]
    elif module.params['short_name']:
        to_find = module.params['short_name']
        found_scopes = [s for s in all_scopes_response if to_find in s['short_name']]
        if module.params['only_dirty']:
            found_scopes = [s for s in found_scopes if s['dirty'] == True]
        result['objects'] = found_scopes
        result['qty_found'] = len(found_scopes)
        if found_scopes:
            result['object'] = found_scopes[0]

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
