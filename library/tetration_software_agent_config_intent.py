#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
author: Brandon Beck (@techbeck03)
description: Enables creation, modification, deletion and query of software agent
  config intent
extends_documentation_fragment: tetration
module: tetration_software_agent_config_intent
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  inventory_config_profile_id:
    description: ID of inventory config profile
    required: true
    type: string
  inventory_filter_id:
    description:
    - ID of inventory filter for associating agent profile
    - Require one of [C(scope_id), C(inventory_filter_name), C(inventory_filter_id)]
    - Mutually exclusive to C(inventory_filter_name)
    type: string
  inventory_filter_name:
    description:
    - Name of inventory filter for associating agent profile
    - Require one of [C(scope_id), C(inventory_filter_name), C(inventory_filter_id)]
    - Mutually exclusive to C(inventory_filter_id)
    - Required together [C(inventory_filter_name), C(inventory_filter_type)]
    type: string
  inventory_filter_type:
    choices: '[inventory, scope]'
    description:
    - Type of inventory filter used for association
    - Required together [C(inventory_filter_name), C(inventory_filter_type)]
    type: string
  root_app_scope_id:
    description: ID of root app scope for tenant to which an agent profile should
      be applied
    type: string
  state:
    choices: '[present, absent, query]'
    default: present
    description: Add, change, remove or query for agent config intents
    required: true
    type: string
  tenant_name:
    description: Tenant name to which an agent config profile should be applied
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

EXAMPLES = r'''
# Add or Modify agent config intent
tetration_software_agent_config_intent:
    tenant_name: ACME
    inventory_config_profile_id: 596d6751497d4f3eb1f1fd2d
    inventory_filter_name: ACME
    inventory_filter_type: scope
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
# Delete agent config intent
tetration_software_agent_config_intent:
    tenant_name: ACME
    inventory_filter_name: ACME
    inventory_filter_type: scope
    inventory_config_profile_id: 596d6751497d4f3eb1f1fd2d
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
# Query agent config intent
tetration_software_agent_config_intent:
    tenant_name: ACME
    inventory_filter_name: ACME
    inventory_filter_type: scope
    inventory_config_profile_id: 596d6751497d4f3eb1f1fd2d
    state: query
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = r'''
---
object:
  contains:
    created_at:
      description: Date this inventory was created (Unix Epoch)
      returned: when C(state) is present or query
      sample: 1500402190
      type: int
    id:
      description: Unique identifier for the agent config intent
      returned: when C(state) is present or query
      sample: 2000
      type: int
    intentory_config_profile_id:
      description: Unique ID of agent config profile
      returned: when C(state) is present or query
      sample: 596d6751497d4f3eb1f1fd2d
      type: string
    inventory_filter_id:
      description: Unique id of the filter associated with intent
      returned: when C(state) is present or query
      sample: 5c493b58755f027da9818750
      type: string
    name:
      description: User provided name for config intent
      returned: when C(state) is present or query
      sample: ACME
      type: string
    updated_at:
      description: Date this inventory filter was last updated (Unix Epoch)
      returned: when C(state) is present or query
      sample: 1500402190
      type: int
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems, iterkeys
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_SCOPES
from ansible.module_utils.tetration.api import TETRATION_API_AGENT_CONFIG_PROFILES
from ansible.module_utils.tetration.api import TETRATION_API_AGENT_CONFIG_INTENTS
from ansible.module_utils.tetration.api import TETRATION_API_INVENTORY_FILTER

def main():
    ''' Main entry point for module execution
    '''
    #
    # Module specific spec
    tetration_spec = dict(
        tenant_name=dict(type='str', required=False),
        root_app_scope_id=dict(type='str', required=False),
        inventory_config_profile_id=dict(type='str', required=True),
        inventory_filter_id=dict(type='str', required=False),
        inventory_filter_name=dict(type='str', required=False),
        inventory_filter_type=dict(type='str', required=False, choices=['inventory', 'scope'])
    )
    # Common spec for tetration modules
    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent', 'query'])
    )

    # Combine specs and include provider parameter
    argument_spec.update(tetration_spec)
    argument_spec.update(TetrationApiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ['inventory_filter_id', 'inventory_filter_name']
        ],
        mutually_exclusive=[
            ['inventory_filter_id', 'inventory_filter_name'],
            ['inventory_filter_id', 'inventory_filter_type']
        ],
        required_together=[
            ['inventory_filter_name', 'inventory_filter_type']
        ]
    )

    # These are all elements we put in our return JSON object for clarity
    tet_module = TetrationApiModule(module)
    result = dict(
        changed=False,
        object=None,
    )
    
    state = module.params['state']
    check_mode = module.check_mode
    tenant_name = module.params['tenant_name']
    root_app_scope_id = module.params['root_app_scope_id']
    inventory_config_profile_id = module.params['inventory_config_profile_id']
    inventory_filter_id = module.params['inventory_filter_id']
    inventory_filter_name = module.params['inventory_filter_name']
    inventory_filter_type = module.params['inventory_filter_type']
    existing_app_scope = None
    existing_config_profile = None
    existing_inventory_filter = None
    existing_config_intent = None

    # =========================================================================
    # Get current state of the object
    if root_app_scope_id:
        existing_app_scope = tet_module.run_method(
            method_name = 'get',
            target = '%s/%s' % (TETRATION_API_SCOPES, root_app_scope_id)
        )
    elif not root_app_scope_id:
        existing_app_scope = tet_module.get_object(
            target = TETRATION_API_SCOPES,
            filter = dict(name=tenant_name)
        )

    if not existing_app_scope:
        if root_app_scope_id:
            module.fail_json(msg='Unable to find existing app scope with id: %s' % root_app_scope_id)
        else:
            module.fail_json(msg='Unable to find existing app scope named: %s' % tenant_name)

    existing_config_profile = tet_module.run_method(
        method_name = 'get',
        target = '%s/%s' % (TETRATION_API_AGENT_CONFIG_PROFILES, inventory_config_profile_id)
    )

    if not existing_config_profile:
        module.fail_json(msg='Unable to find existing config profile with id: %s' % inventory_config_profile_id)

    if inventory_filter_type == 'inventory':
        if inventory_filter_id:
            existing_inventory_filter = run_method(
                method_name = 'get',
                target = '%s/%s' % (TETRATION_API_INVENTORY_FILTER, inventory_filter_id),
            )
        else:
            app_scopes = tet_module.get_object(
                target = TETRATION_API_SCOPES,
                filter = dict(root_app_scope_id = existing_app_scope['root_app_scope_id']),
                allow_multiple = True
            )
            scope_ids = [ scope['id'] for scope in app_scopes ]
            inventory_filters = tet_module.run_method(
                method_name = 'get',
                target = TETRATION_API_INVENTORY_FILTER,
            )
            if inventory_filters:
                inventory_filters = [ valid_filter for valid_filter in inventory_filters if valid_filter['app_scope_id'] in scope_ids and valid_filter['name'] == inventory_filter_name ]
                existing_inventory_filter = inventory_filters[0] if len(inventory_filters) == 1 else None
            else:
                existing_inventory_filter = None
        if not existing_inventory_filter:
            if inventory_filter_id:
                module.fail_json(msg='Unable to find inventory filter matching id: %s' % inventory_filter_id)
            else:
                module.fail_json(msg='Unable to find inventory filter named: %s' % inventory_filter_name)

    elif inventory_filter_type == 'scope':
        if inventory_filter_id:
            existing_inventory_filter = run_method(
                method_name = 'get',
                target = '%s/%s' % (TETRATION_API_SCOPES, inventory_filter_id),
            )
        else:
            existing_inventory_filter = tet_module.get_object(
                target = TETRATION_API_SCOPES,
                filter = dict(
                    root_app_scope_id = existing_app_scope['root_app_scope_id'],
                    name = inventory_filter_name
                )
            )
        if not existing_inventory_filter:
            if inventory_filter_id:
                module.fail_json(msg='Unable to find scope matching id: %s' % inventory_filter_id)
            else:
                module.fail_json(msg='Unable to find scope named: %s' % inventory_filter_name)

    existing_config_intent = tet_module.get_object(
        target = TETRATION_API_AGENT_CONFIG_INTENTS,
        filter = dict(
            inventory_filter_id = existing_inventory_filter['id'],
            inventory_config_profile_id = inventory_config_profile_id
        )
    )

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':
        new_object = dict(
            inventory_filter_id = existing_inventory_filter['id'],
            inventory_config_profile_id = inventory_config_profile_id
        )
        if not existing_config_intent:
            if not check_mode:
                tet_module.run_method(
                    method_name = 'post',
                    target = TETRATION_API_AGENT_CONFIG_INTENTS,
                    req_payload = new_object
                )
            result['object'] = new_object
            result['changed'] = True
        else:
            result['object'] = existing_config_profile

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif module.params['state'] in 'absent':
        if existing_config_intent:
            if not check_mode:
                tet_module.run_method(
                    method_name = 'delete',
                    target = '%s/%s' % (TETRATION_API_AGENT_CONFIG_INTENTS, existing_config_intent['id'])
                )
            result['changed'] = True
    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    else:
        result['object'] = existing_config_intent
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()
