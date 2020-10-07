ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tetration_software_agent_config_profile

short description: Enables creation, modification, deletion and query of software agent
  config profiles

version_added: '2.9'

description: Enables creation, modification, deletion and query of software agent
  config profiles

options:
    allow_broadcast:
        default: 'True'
        description: Whether or not broadcast traffic should be allowed
        type: bool
    allow_multicast:
        default: 'True'
        description: Whether or not broadcast traffic should be allowed
        type: bool
    auto_upgrade_opt_out:
        default: 'True'
        description: If True, agents are not auto-upgraded during upgrade of Tetration
          cluster
        type: bool
    cpu_quota_mode:
        choices: [0, 1, 2]
        default: 1
        description: 0=disabled 1=Adjusted 2=To
        type: int
    cpu_quota_pct:
        default: 3
        description: The amount of CPU quota to give to agent on the end host
        type: int
    data_plane_disabled:
        default: 'False'
        description: If true, agent stops reporting flows to Tetration
        type: bool
    enable_cache_sidechannel:
        default: 'False'
        description: Whether or not sidechannel detection is enabled
        type: bool
    enable_forensic:
        default: 'False'
        description: Whether or not forensics is enabled
        type: bool
    enable_meltdown:
        default: 'False'
        description: Whether or not meltdown detection is enabled
        type: bool
    enable_pid_lookup:
        default: 'False'
        description: Whether or not pid lookup for flow search is enabled
        type: bool
    enforcement_disabled:
        default: 'True'
        description: If True, enforcement is disabled
        type: bool
    name:
        description: User provided name of software agent profile
        required: true
        type: string
    preserve_existing_rules:
        default: 'False'
        description: If True, existing firewall rules are preserved
        type: bool
    root_app_scope_id:
        description: ID of root app scope for tenant to which an agent profile should
          be applied
        type: string
    state:
        choices: [present, absent, query]
        default: present
        description: Add, change, remove or query for agent config profiles
        required: true
        type: string
    tenant_name:
        description: Tenant name to which an agent config profile should be applied
        type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.

requirements:
- requests

author:
  - Brandon Beck (@techbeck03)
  - Joe Jacobs (@joej164)

'''

EXAMPLES = '''
# Add or Modify agent config profile
tetration_software_agent_config_profile:
    name: Enforcement Enabled
    tenant_name: ACME
    allow_broadcast: True
    allow_multicast: True
    auto_upgrade_opt_out: False
    cpu_quota_mode: 1
    cpu_quota_pct: 3
    data_plane_disabled: False
    enable_cache_sidechannel: False
    enable_forensic: True
    enable_meltdown: False
    enable_pid_lookup: True
    enforcement_disabled: False
    preserve_existing_rules: False
    state: present
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete agent config profile
tetration_software_agent_config_profile:
    name: Enforcement Enabled
    tenant_name: ACME
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query agent config profile
tetration_software_agent_config_profile:
    name: Enforcement Enabled
    tenant_name: ACME
    state: query
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  contains:
    allow_broadcast:
      description: Whether or not broadcast traffic should be allowed
      returned: when C(state) is present or query
      sample: 'True'
      type: bool
    allow_multicast:
      description: Whether or not broadcast traffic should be allowed
      returned: when C(state) is present or query
      sample: 'True'
      type: bool
    auto_upgrade_opt_out:
      description: If True, agents are not auto-upgraded during upgrade of Tetration
        cluster
      returned: when C(state) is present or query
      sample: 'False'
      type: bool
    cpu_quota_mode:
      description: 0=disabled 1=Adjusted 2=Top
      returned: when C(state) is present or query
      sample: 1
      type: bool
    cpu_quota_pct:
      description: The amount of CPU quota to give to agent on the end host (pct)
      returned: when C(state) is present or query
      sample: 3
      type: int
    cpu_quota_us:
      description: The amount of CPU quota to give to agent on the end host (us)
      returned: when C(state) is present or query
      sample: 30000
      type: int
    data_plane_disabled:
      description: If true, agent stops reporting flows to Tetration
      returned: when C(state) is present or query
      sample: 'False'
      type: bool
    enable_cache_sidechannel:
      description: Whether or not sidechannel detection is enabled
      returned: when C(state) is present or query
      sample: 'False'
      type: bool
    enable_forensic:
      description: Whether or not forensics is enabled
      returned: when C(state) is present or query
      sample: 'True'
      type: bool
    enable_meltdown:
      description: Whether or not meltdown detection is enabled
      returned: when C(state) is present or query
      sample: 'False'
      type: bool
    enable_pid_lookup:
      description: Whether or not pid lookup for flow search is enabled
      returned: when C(state) is present or query
      sample: 'True'
      type: bool
    enforcement_disabled:
      description: If True, enforcement is disabled
      returned: when C(state) is present or query
      sample: 'False'
      type: bool
    id:
      description: Unique identifier for the agent config intent
      returned: when C(state) is present or query
      sample: 2000
      type: int
    name:
      description: User provided name for config intent
      returned: when C(state) is present or query
      sample: Enforcement Enabled
      type: string
    preserve_existing_rules:
      description: If True, existing firewall rules are preserved
      returned: when C(state) is present or query
      sample: 'False'
      type: bool
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_AGENT_CONFIG_PROFILES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def main():
    ''' Main entry point for module execution
    '''
    #
    # Module specific spec
    module_args = dict(
        name=dict(type='str', required=True),
        root_app_scope_id=dict(type='str', required=False),
        root_app_scope_name=dict(type='str', required=False),
        allow_broadcast=dict(type='bool', required=False, default=True),
        allow_multicast=dict(type='bool', required=False, default=True),
        auto_upgrade_opt_out=dict(type='bool', required=False, default=True),
        cpu_quota_mode=dict(type='int', required=False, default=1, choices=[0, 1, 2]),
        cpu_quota_pct=dict(type='int', required=False, default=3),
        data_plane_disabled=dict(type='bool', required=False, default=False),
        enable_cache_sidechannel=dict(type='bool', required=False, default=False),
        enable_forensics=dict(type='bool', required=False, default=False),
        enable_meltdown=dict(type='bool', required=False, default=False),
        enable_pid_lookup=dict(type='bool', required=False, default=False),
        enforcement_disabled=dict(type='bool', required=False, default=True),
        preserve_existing_rules=dict(type='bool', required=False, default=False),
        state=dict(default='present', choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # Combine specs and include provider parameter

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['root_app_scope_id', 'root_app_scope_name']
        ],
        mutually_exclusive=[
            ['root_app_scope_id', 'root_app_scope_name']
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
    name = module.params['name']
    root_app_scope_id = module.params['root_app_scope_id']
    tenant_name = module.params['tenant_name']
    allow_broadcast = module.params['allow_broadcast']
    allow_multicast = module.params['allow_multicast']
    auto_upgrade_opt_out = module.params['auto_upgrade_opt_out']
    cpu_quota_mode = module.params['cpu_quota_mode']
    cpu_quota_pct = module.params['cpu_quota_pct']
    data_plane_disabled = module.params['data_plane_disabled']
    enable_cache_sidechannel = module.params['enable_cache_sidechannel']
    enable_forensics = module.params['enable_forensics']
    enable_meltdown = module.params['enable_meltdown']
    enable_pid_lookup = module.params['enable_pid_lookup']
    enforcement_disabled = module.params['enforcement_disabled']
    preserve_existing_rules = module.params['preserve_existing_rules']
    existing_app_scope = None
    existing_config_profile = None
    agent_options = [
        'allow_broadcast',
        'allow_multicast',
        'auto_upgrade_opt_out',
        'cpu_quota_mode',
        'cpu_quota_pct',
        'data_plane_disabled',
        'enable_cache_sidechannel',
        'enable_forensics',
        'enable_meltdown',
        'enable_pid_lookup',
        'enforcement_disabled',
        'preserve_existing_rules'
    ]
    agent_update_remove_keys = [
        'preserve_existing_rules'
    ]

    # =========================================================================
    # Get current state of the object
    if root_app_scope_id:
        existing_app_scope = tet_module.run_method(
            method_name='get',
            target='%s/%s' % (TETRATION_API_SCOPES, root_app_scope_id)
        )
    elif not root_app_scope_id:
        existing_app_scope = tet_module.get_object(
            target=TETRATION_API_SCOPES,
            filter=dict(name=tenant_name)
        )

    if not existing_app_scope:
        module.fail_json(msg='Unable to find existing app scope named: %s' % tenant_name)

    existing_profile_filter = dict(name=name)
    if existing_app_scope['name'] != 'Default':
        existing_profile_filter['root_app_scope_id'] = existing_app_scope['root_app_scope_id']
    existing_config_profile = tet_module.get_object(
        target=TETRATION_API_AGENT_CONFIG_PROFILES,
        filter=existing_profile_filter
    )

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':
        new_object = dict(
            root_app_scope_id=existing_app_scope['id'],
            name=name,
        )
        for option in agent_options:
            new_object[option] = module.params.get(option)
        if not existing_config_profile:
            if not check_mode:
                result['object'] = tet_module.run_method(
                    method_name='post',
                    target=TETRATION_API_AGENT_CONFIG_PROFILES,
                    req_payload=new_object
                )
            else:
                result['object'] = new_object
            result['changed'] = True
        else:
            for option in agent_update_remove_keys:
                del new_object[option]
            result['changed'] = tet_module.filter_object(new_object, existing_config_profile, check_only=True)
            if not check_mode:
                result['object'] = tet_module.run_method(
                    method_name='put',
                    target='%s/%s' % (TETRATION_API_AGENT_CONFIG_PROFILES, existing_config_profile['id']),
                    req_payload=new_object
                )
            else:
                result['object'] = new_object

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif module.params['state'] in 'absent':
        if existing_config_profile:
            if not check_mode:
                tet_module.run_method(
                    method_name='delete',
                    target='%s/%s' % (TETRATION_API_AGENT_CONFIG_PROFILES, existing_config_profile['id'])
                )
            result['changed'] = True
    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    else:
        result['object'] = existing_config_profile

    module.exit_json(**result)


if __name__ == '__main__':
    main()
