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
        description:
        - Whether or not broadcast traffic should be allowed
        - Matching GUI Element - Enforcement -> Allow Broadcast
        type: bool
    allow_link_local:
        description:
        - If True, Adds rules to the firewall to always allow link local addresses’ traffic on the workload.
        - Matching GUI Element - Enforcement -> Allow Link Local Address 
        type: bool
    allow_multicast:
        description:
        - Whether or not broadcast traffic should be allowed
        - Matching GUI Element - Enforcement -> Allow Multicast 
        type: bool
    auto_upgrade_opt_out:
        description:
        - If True, agents are not auto-upgraded during upgrade of Tetration cluster
        - Matching GUI Element - Visibility -> Auto-Upgrade
        type: bool
    cpu_quota_mode:
        choices: [0, 1, 2]
        description:
        - 0=disabled 1=Adjusted 2=Top
        - ---
        - 'If mode Adjusted: The CPU limit is adjusted according to the number of CPUs on the system.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system, selecting
        - this mode means that agent is allowed to use a total of 30% (measured by top).
        - ---
        - 'If mode Top: The CPU limit value would match the top view on average.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system.
        - The cpu usuage would still be 3%.
        - This is a fairly restrictive mode and should be used only when necessary.
        - ---
        - 'If mode Disabled: The CPU limit feature is disabled. The agent will use CPU resources permitted by the OS.'
        - ---
        - Matching GUI Element - Visibility -> CPU Quota Mode 
        type: int
    cpu_quota_pct:
        description:
        - The amount of CPU quota to give to agent on the end host
        - Matching GUI Element - Visibility -> CPU Quota Mode Percent
        - Mutually exclusive [C(cpu_quota_pct), C(cpu_quota_us)]
        - 'Valid values: 1 to 100'
        type: int
    cpu_quota_us:
        description:
        - The amount of CPU quota to give to agent on the end host
        - This is much more granular than C(cpu_quota_pct)
        - Matching GUI Element - Visibility -> CPU Quota Mode Percent
        - Mutually exclusive [C(cpu_quota_pct), C(cpu_quota_us)]
        - 'Valid values: 10000 to 1000000'
        - Value of 10000 equals 1 percent in the GUI
        - Value of 1000000 equals 100 percent in the GUI
        type: int
    data_plane_disabled:
        description:
        - If true, agent stops reporting flows to Tetration
        - Matching GUI Element - Visibility -> Data Plane 
        type: bool
    enable_dns:
        description:
        - This a placeholder for a future feature 
        - You can changed the value and it will update the profile
        - At this time has not impact on the Profile 
        type: bool
    enable_forensic:
        description:
        - Whether or not forensics is enabled
        - Matching GUI Element - Forensics -> Forensics 
        type: bool
    enable_meltdown:
        description:
        - Whether or not meltdown detection is enabled
        - Matching GUI Element - Forensics -> Meltdown Exploit Detection
        type: bool
    enable_pid_lookup:
        description:
        - Whether or not pid lookup for flow search is enabled
        - Matching GUI Element - Visability -> PID Lookup 
        type: bool
    enforcement_cpu_quota_mode:
        choices: [0, 1, 2]
        description:
        - 0=disabled 1=Adjusted 2=Top
        - ---
        - 'If mode Adjusted: The CPU limit is adjusted according to the number of CPUs on the system.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system, selecting
        - this mode means that agent is allowed to use a total of 30% (measured by top).
        - ---
        - 'If mode Top: The CPU limit value would match the top view on average.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system.
        - The cpu usuage would still be 3%.
        - This is a fairly restrictive mode and should be used only when necessary.
        - ---
        - 'If mode Disabled: The CPU limit feature is disabled. The agent will use CPU resources permitted by the OS.'
        - ---
        - Matching GUI Element - Visibility -> CPU Quota Mode 
        type: int
    enforcement_cpu_quota_pct:
        description:
        - The amount of CPU quota to give to agent on the end host
        - Matching GUI Element - Enforcement -> CPU Quota Mode Percent
        - Mutually exclusive [C(enforcement_cpu_quota_pct), C(enforcement_cpu_quota_us)]
        - 'Valid values: 1 to 100'
        type: int
    enforcement_cpu_quota_us:
        description:
        - The amount of CPU quota to give to agent on the end host
        - This is much more granular than C(enforcement_cpu_quota_pct)
        - Matching GUI Element - Enforcement -> CPU Quota Mode Percent
        - Mutually exclusive [C(cpu_quota_pct), C(cpu_quota_us)]
        - 'Valid values: 10000 to 1000000'
        - Value of 10000 equals 1 percent in the GUI
        - Value of 1000000 equals 100 percent in the GUI
        type: int
    enforcement_disabled:
        description:
        - If True, enforcement is disabled
        - Matching GUI Element - Enforcement -> Enforcement
        type: bool
    enforcement_max_rss_limit:
        description:
        - Specify the memory limit in bytes that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Enforcement -> Memory Quota Limit MB 
        - Mutually exclusive [C(enforcement_max_rss_limit), C(enforcement_max_rss_limit_mb)]
        - 'Valid values: 134217728 (128MB) to 2147483648 (2048M)'
        type: bool
    enforcement_max_rss_limit_mb:
        description:
        - Specify the memory limit in MegaBytes (MB) that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Enforcement -> Memory Quota Limit MB 
        - Mutually exclusive [C(enforcement_max_rss_limit), C(enforcement_max_rss_limit_mb)]
        - 'Valid values: 128 (MB) to 2048 (MB)'
        type: bool
    forensics_cpu_quota_mode:
        choices: [0, 1, 2]
        description:
        - 0=disabled 1=Adjusted 2=Top
        - ---
        - 'If mode Adjusted: The CPU limit is adjusted according to the number of CPUs on the system.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system, selecting
        - this mode means that agent is allowed to use a total of 30% (measured by top).
        - ---
        - 'If mode Top: The CPU limit value would match the top view on average.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system.
        - The cpu usuage would still be 3%.
        - This is a fairly restrictive mode and should be used only when necessary.
        - ---
        - 'If mode Disabled: The CPU limit feature is disabled. The agent will use CPU resources permitted by the OS.'
        - ---
        - Matching GUI Element - Visibility -> CPU Quota Mode 
        type: int
    forensics_cpu_quota_pct:
        description:
        - The amount of CPU quota to give to agent on the end host
        - Matching GUI Element - Forensics -> CPU Quota Mode Percent
        - Mutually exclusive [C(forensics_cpu_quota_pct), C(forensics_cpu_quota_us)]
        - 'Valid values: 1 to 100'
        type: int
    forensics_cpu_quota_us:
        description:
        - The amount of CPU quota to give to agent on the end host
        - This is much more granular than C(forensics_cpu_quota_pct)
        - Matching GUI Element - Forensics -> CPU Quota Mode Percent
        - Mutually exclusive [C(forensics_cpu_quota_pct), C(forensics_cpu_quota_us)]
        - 'Valid values: 10000 to 1000000'
        - Value of 10000 equals 1 percent in the GUI
        - Value of 1000000 equals 100 percent in the GUI
        type: int
    forensics_mem_quota_bytes:
        description:
        - Specify the memory limit in bytes that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Forensics -> Memory Quota Limit MB 
        - Mutually exclusive [C(forensics_mem_quota_bytes), C(forensics_mem_quota_mb)]
        - 'Valid values: 134217728 (128MB) to 2147483648 (2048M)'
        type: bool
    forensics_mem_quota_mb:
        description:
        - Specify the memory limit in MegaBytes (MB) that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Forensics -> Memory Quota Limit MB 
        - Mutually exclusive [C(forensics_mem_quota_bytes), C(forensics_mem_quota_mb)]
        - 'Valid values: 128 (MB) to 2048 (MB)'
        type: bool
    id:
        description:
        - The ID of the policy
        - Required when updating the name of a profile, otherwise is not needed
        - Can be used to identify a profile instead of using the name field
        type: bool
    max_rss_limit:
        description:
        - Specify the memory limit in bytes that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Visability -> Memory Quota Limit MB 
        - Mutually exclusive [C(max_rss_limit), C(max_rss_limit_mb)]
        - 'Valid values: 209715200 (200MB) to 2147483648 (2048M)'
        type: bool
    max_rss_limit_mb:
        description:
        - Specify the memory limit in MegaBytes (MB) that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Visability -> Memory Quota Limit MB 
        - Mutually exclusive [C(max_rss_limit), C(max_rss_limit_mb)]
        - 'Valid values: 200 (MB) to 2048 (MB)'
        type: bool
    name:
        description:
        - User provided name of software agent config profile
        - Required when creating a new profile
        required: false
        type: string
    preserve_existing_rules:
        description:
        - If True, existing firewall rules are preserved
        - Matching GUI Element - Enforcement -> Preserve Rules 
        type: bool
    root_app_scope_id:
        description:
        - ID of root app scope for tenant to which an agent profile should be applied
        - Mutually exculusive [C(root_app_scope_id), C(root_app_scope_name)]
        type: string
    root_app_scope_name:
        description:
        - Name of root app scope for tenant to which an agent profile should be applied
        - Mutually exculusive [C(root_app_scope_id), C(root_app_scope_name)]
        type: string
    state:
        choices: [present, absent, query]
        description: Add, change, remove or query for agent config profiles
        required: true
        type: string

extends_documentation_fragment: tetration_doc_common

notes:
- Requires the `requests` Python module.
- For defaults, look at the `Default` profile in the system.  All new profiles are modeled from that unless parameter specified.

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
    root_app_scope_name: ACME
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
    root_app_scope_name: ACME
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query agent config profile
tetration_software_agent_config_profile:
    name: Enforcement Enabled
    root_app_scope_name: ACME
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
        description:
        - Whether or not broadcast traffic should be allowed
        - Matching GUI Element - Enforcement -> Allow Broadcast
        type: bool
    allow_link_local:
        description:
        - If True, Adds rules to the firewall to always allow link local addresses’ traffic on the workload.
        - Matching GUI Element - Enforcement -> Allow Link Local Address 
        type: bool
    allow_multicast:
        description:
        - Whether or not broadcast traffic should be allowed
        - Matching GUI Element - Enforcement -> Allow Multicast 
        type: bool
    auto_upgrade_opt_out:
        description:
        - If True, agents are not auto-upgraded during upgrade of Tetration cluster
        - Matching GUI Element - Visibility -> Auto-Upgrade
        type: bool
    cpu_quota_mode:
        choices: [0, 1, 2]
        description:
        - 0=disabled 1=Adjusted 2=Top
        - ---
        - 'If mode Adjusted: The CPU limit is adjusted according to the number of CPUs on the system.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system, selecting
        - this mode means that agent is allowed to use a total of 30% (measured by top).
        - ---
        - 'If mode Top: The CPU limit value would match the top view on average.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system.
        - The cpu usuage would still be 3%.
        - This is a fairly restrictive mode and should be used only when necessary.
        - ---
        - 'If mode Disabled: The CPU limit feature is disabled. The agent will use CPU resources permitted by the OS.'
        - ---
        - Matching GUI Element - Visibility -> CPU Quota Mode 
        type: int
    cpu_quota_pct:
        description:
        - The amount of CPU quota to give to agent on the end host
        - Matching GUI Element - Visibility -> CPU Quota Mode Percent
        - Mutually exclusive [C(cpu_quota_pct), C(cpu_quota_us)]
        - 'Valid values: 1 to 100'
        type: int
    cpu_quota_us:
        description:
        - The amount of CPU quota to give to agent on the end host
        - This is much more granular than C(cpu_quota_pct)
        - Matching GUI Element - Visibility -> CPU Quota Mode Percent
        - Mutually exclusive [C(cpu_quota_pct), C(cpu_quota_us)]
        - 'Valid values: 10000 to 1000000'
        - Value of 10000 equals 1 percent in the GUI
        - Value of 1000000 equals 100 percent in the GUI
        type: int
    data_plane_disabled:
        description:
        - If true, agent stops reporting flows to Tetration
        - Matching GUI Element - Visibility -> Data Plane 
        type: bool
    enable_dns:
        description:
        - This a placeholder for a future feature 
        - You can changed the value and it will update the profile
        - At this time has not impact on the Profile 
        type: bool
    enable_forensic:
        description:
        - Whether or not forensics is enabled
        - Matching GUI Element - Forensics -> Forensics 
        type: bool
    enable_meltdown:
        description:
        - Whether or not meltdown detection is enabled
        - Matching GUI Element - Forensics -> Meltdown Exploit Detection
        type: bool
    enable_pid_lookup:
        description:
        - Whether or not pid lookup for flow search is enabled
        - Matching GUI Element - Visability -> PID Lookup 
        type: bool
    enforcement_cpu_quota_mode:
        choices: [0, 1, 2]
        description:
        - 0=disabled 1=Adjusted 2=Top
        - ---
        - 'If mode Adjusted: The CPU limit is adjusted according to the number of CPUs on the system.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system, selecting
        - this mode means that agent is allowed to use a total of 30% (measured by top).
        - ---
        - 'If mode Top: The CPU limit value would match the top view on average.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system.
        - The cpu usuage would still be 3%.
        - This is a fairly restrictive mode and should be used only when necessary.
        - ---
        - 'If mode Disabled: The CPU limit feature is disabled. The agent will use CPU resources permitted by the OS.'
        - ---
        - Matching GUI Element - Visibility -> CPU Quota Mode 
        type: int
    enforcement_cpu_quota_pct:
        description:
        - The amount of CPU quota to give to agent on the end host
        - Matching GUI Element - Enforcement -> CPU Quota Mode Percent
        - Mutually exclusive [C(enforcement_cpu_quota_pct), C(enforcement_cpu_quota_us)]
        - 'Valid values: 1 to 100'
        type: int
    enforcement_cpu_quota_us:
        description:
        - The amount of CPU quota to give to agent on the end host
        - This is much more granular than C(enforcement_cpu_quota_pct)
        - Matching GUI Element - Enforcement -> CPU Quota Mode Percent
        - Mutually exclusive [C(cpu_quota_pct), C(cpu_quota_us)]
        - 'Valid values: 10000 to 1000000'
        - Value of 10000 equals 1 percent in the GUI
        - Value of 1000000 equals 100 percent in the GUI
        type: int
    enforcement_disabled:
        description:
        - If True, enforcement is disabled
        - Matching GUI Element - Enforcement -> Enforcement
        type: bool
    enforcement_max_rss_limit:
        description:
        - Specify the memory limit in bytes that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Enforcement -> Memory Quota Limit MB 
        - Mutually exclusive [C(enforcement_max_rss_limit), C(enforcement_max_rss_limit_mb)]
        - 'Valid values: 134217728 (128MB) to 2147483648 (2048M)'
        type: bool
    enforcement_max_rss_limit_mb:
        description:
        - Specify the memory limit in MegaBytes (MB) that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Enforcement -> Memory Quota Limit MB 
        - Mutually exclusive [C(enforcement_max_rss_limit), C(enforcement_max_rss_limit_mb)]
        - 'Valid values: 128 (MB) to 2048 (MB)'
        type: bool
    forensics_cpu_quota_mode:
        choices: [0, 1, 2]
        description:
        - 0=disabled 1=Adjusted 2=Top
        - ---
        - 'If mode Adjusted: The CPU limit is adjusted according to the number of CPUs on the system.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system, selecting
        - this mode means that agent is allowed to use a total of 30% (measured by top).
        - ---
        - 'If mode Top: The CPU limit value would match the top view on average.'
        - For example, if the CPU limit is set to 3% and there are 10 CPUs in the system.
        - The cpu usuage would still be 3%.
        - This is a fairly restrictive mode and should be used only when necessary.
        - ---
        - 'If mode Disabled: The CPU limit feature is disabled. The agent will use CPU resources permitted by the OS.'
        - ---
        - Matching GUI Element - Visibility -> CPU Quota Mode 
        type: int
    forensics_cpu_quota_pct:
        description:
        - The amount of CPU quota to give to agent on the end host
        - Matching GUI Element - Forensics -> CPU Quota Mode Percent
        - Mutually exclusive [C(forensics_cpu_quota_pct), C(forensics_cpu_quota_us)]
        - 'Valid values: 1 to 100'
        type: int
    forensics_cpu_quota_us:
        description:
        - The amount of CPU quota to give to agent on the end host
        - This is much more granular than C(forensics_cpu_quota_pct)
        - Matching GUI Element - Forensics -> CPU Quota Mode Percent
        - Mutually exclusive [C(forensics_cpu_quota_pct), C(forensics_cpu_quota_us)]
        - 'Valid values: 10000 to 1000000'
        - Value of 10000 equals 1 percent in the GUI
        - Value of 1000000 equals 100 percent in the GUI
        type: int
    forensics_mem_quota_bytes:
        description:
        - Specify the memory limit in bytes that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Forensics -> Memory Quota Limit MB 
        - Mutually exclusive [C(forensics_mem_quota_bytes), C(forensics_mem_quota_mb)]
        - 'Valid values: 134217728 (128MB) to 2147483648 (2048M)'
        type: bool
    forensics_mem_quota_mb:
        description:
        - Specify the memory limit in MegaBytes (MB) that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Forensics -> Memory Quota Limit MB 
        - Mutually exclusive [C(forensics_mem_quota_bytes), C(forensics_mem_quota_mb)]
        - 'Valid values: 128 (MB) to 2048 (MB)'
        type: bool
    id:
        description:
        - The ID of the policy
        - Required when updating the name of a profile, otherwise is not needed
        - Can be used to identify a profile instead of using the name field
        type: bool
    max_rss_limit:
        description:
        - Specify the memory limit in bytes that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Visability -> Memory Quota Limit MB 
        - Mutually exclusive [C(max_rss_limit), C(max_rss_limit_mb)]
        - 'Valid values: 209715200 (200MB) to 2147483648 (2048M)'
        type: bool
    max_rss_limit_mb:
        description:
        - Specify the memory limit in MegaBytes (MB) that the process is allowed to use.
        - If the process hits this limit, it will restart.
        - ---
        - Matching GUI Element - Visability -> Memory Quota Limit MB 
        - Mutually exclusive [C(max_rss_limit), C(max_rss_limit_mb)]
        - 'Valid values: 200 (MB) to 2048 (MB)'
        type: bool
    name:
        description:
        - User provided name of software agent config profile
        - Required when creating a new profile
        required: false
        type: string
    preserve_existing_rules:
        description:
        - If True, existing firewall rules are preserved
        - Matching GUI Element - Enforcement -> Preserve Rules 
        - Due to a bug, this parameter is not returned at the time of writing this module
        type: bool
    root_app_scope_id:
        description:
        - ID of root app scope for tenant to which an agent profile should be applied
        - Mutually exculusive [C(root_app_scope_id), C(root_app_scope_name)]
        type: string
    updated_at:
        description:
        - time stamp of the last time this profile was updated
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration import TetrationApiModule
from ansible.module_utils.tetration_constants import TETRATION_API_SCOPES
from ansible.module_utils.tetration_constants import TETRATION_API_AGENT_CONFIG_PROFILES
from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC


def validate_ranges(params_to_validate, all_params, low_value, high_value):
    invalid_pct_params = []
    for param in params_to_validate:
        if all_params[param] is not None and all_params[param] not in range(low_value, high_value + 1):
            invalid_pct_params.append(param)

    return invalid_pct_params


def main():
    ''' Main entry point for module execution
    '''
    #
    # Module specific spec
    module_args = dict(
        name=dict(type='str', required=False),
        id=dict(type='str', required=False),
        root_app_scope_id=dict(type='str', required=False),
        root_app_scope_name=dict(type='str', required=False),
        allow_broadcast=dict(type='bool', required=False),
        allow_link_local=dict(type='bool', required=False),
        allow_multicast=dict(type='bool', required=False),
        auto_upgrade_opt_out=dict(type='bool', required=False),
        cpu_quota_mode=dict(type='int', required=False, choices=[0, 1, 2]),
        cpu_quota_pct=dict(type='int', required=False),
        cpu_quota_us=dict(type='int', required=False),
        data_plane_disabled=dict(type='bool', required=False),
        enable_dns=dict(type='bool', required=False),
        enable_forensics=dict(type='bool', required=False),
        enable_meltdown=dict(type='bool', required=False),
        enable_pid_lookup=dict(type='bool', required=False),
        enforcement_cpu_quota_mode=dict(type='int', required=False, choices=[0, 1, 2]),
        enforcement_cpu_quota_pct=dict(type='int', required=False),
        enforcement_cpu_quota_us=dict(type='int', required=False),
        enforcement_disabled=dict(type='bool', required=False),
        enforcement_max_rss_limit=dict(type='int', required=False),
        enforcement_max_rss_limit_mb=dict(type='int', required=False),
        forensics_cpu_quota_mode=dict(type='int', required=False, choices=[0, 1, 2]),
        forensics_cpu_quota_pct=dict(type='int', required=False),
        forensics_cpu_quota_us=dict(type='int', required=False),
        forensics_mem_quota_bytes=dict(type='int', required=False),
        forensics_mem_quota_mb=dict(type='int', required=False),
        max_rss_limit=dict(type='int', required=False),
        max_rss_limit_mb=dict(type='int', required=False),
        preserve_existing_rules=dict(type='bool', required=False),
        state=dict(choices=['present', 'absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # Building custom error handling to display custom error messages

    # Combine specs and include provider parameter
    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ['root_app_scope_id', 'root_app_scope_name'],
            ['name', 'id']
        ],
        mutually_exclusive=[
            ['root_app_scope_id', 'root_app_scope_name'],
            ['cpu_quota_pct', 'cpu_quota_us'],
            ['enforcement_cpu_quota_pct', 'enforcement_cpu_quota_us'],
            ['forensics_cpu_quota_pct', 'forensics_cpu_quota_us'],
            ['enforcement_max_rss_limit', 'enforcement_max_rss_limit_mb'],
            ['forensics_mem_quota_bytes', 'forensics_mem_quota_mb'],
            ['max_rss_limit', 'max_rss_limit_mb'],
        ]
    )

    if module.params['name'] == 'Default':
        module.fail_json(msg='Cannot modify the default agent profile')

    # Verify the following modules have valid inputs between 1 and 100% inclusive
    percent_params = ['cpu_quota_pct', 'enforcement_cpu_quota_pct', 'forensics_cpu_quota_pct']
    invalid_percent_params = validate_ranges(percent_params, module.params, low_value=1, high_value=100)
    if invalid_percent_params:
        module.fail_json(msg=f'The following params need to be between 1 and 100 inclusive: {invalid_percent_params}')

    # Verify the following modules have valid inputs between 10,000 and 1,000,000 inclusive
    us_params = ['cpu_quota_us', 'enforcement_cpu_quota_us', 'forensics_cpu_quota_us']
    invalid_us_params = validate_ranges(us_params, module.params, low_value=10000, high_value=100000)
    if invalid_us_params:
        module.fail_json(msg=f'The following params need to be between 10,000 and 1,000,000 inclusive: {invalid_us_params}')

    # Verify the following modules have valid inputs between 128 and 2048 inclusive
    mb_params = ['enforcement_max_rss_limit_mb', 'forensics_mem_quota_mb']
    invalid_mb_params = validate_ranges(mb_params, module.params, low_value=128, high_value=2048)
    if invalid_mb_params:
        module.fail_json(msg=f'The following params need to be between 128 and 2048 inclusive: {invalid_mb_params}')

    # Verify the following modules have valid inputs between 200 and 2048 inclusive
    vis_mb_params = ['max_rss_limit_mb']
    invalid_vis_mb_params = validate_ranges(vis_mb_params, module.params, low_value=200, high_value=2048)
    if invalid_vis_mb_params:
        module.fail_json(msg=f'The following params need to be between 200 and 2048 inclusive: {invalid_vis_mb_params}')

    # Verify the following modules have valid inputs between 134,217,728 and 2,147,483,649 inclusive
    bytes_params = ['enforcement_max_rss_limit', 'forensics_mem_quota_bytes']
    invalid_bytes_params = validate_ranges(bytes_params, module.params, low_value=134217728, high_value=2147483649)
    if invalid_bytes_params:
        module.fail_json(
            msg=f'The following params need to be between 134,217,728 and 2,147,483,649 inclusive: {invalid_bytes_params}')

    # Verify the following modules have valid inputs between 209,715,200 and 2,147,483,649 inclusive
    vis_bytes_params = ['max_rss_limit']
    invalid_vis_bytes_params = validate_ranges(vis_bytes_params, module.params, low_value=209715200, high_value=2147483649)
    if invalid_vis_bytes_params:
        module.fail_json(
            msg=f'The following params need to be between 209,715,200 and 2,147,483,649 inclusive: {invalid_vis_bytes_params}')

    tet_module = TetrationApiModule(module)
    # These are all elements we put in our return JSON object for clarity
    result = {
        'changed': False,
        'object': {},
    }

    # =========================================================================
    # Get current state of the object
    app_scopes = tet_module.run_method('GET', TETRATION_API_SCOPES)
    app_scope_dict = {s['name']: s['id'] for s in app_scopes}

    existing_app_scope_id = None
    if module.params['root_app_scope_id'] in app_scope_dict.values():
        existing_app_scope_id = module.params['root_app_scope_id']
    else:
        scope_name = module.params['root_app_scope_name']
        existing_app_scope_id = app_scope_dict.get(scope_name)

    if not existing_app_scope_id:
        if module.params['app_scope_id']:
            module.fail_json(msg=f"Unable to find existing app scope id: {module.params['app_scope_id']}")
        else:
            module.fail_json(msg=f"Unable to find existing app scope named: {module.params['app_scope_name']}")

    existing_profiles = tet_module.run_method('GET', TETRATION_API_AGENT_CONFIG_PROFILES)

    existing_profile = None

    for profile in existing_profiles:
        if module.params['id'] == profile['id']:
            existing_profile = profile
        elif module.params['name'] == profile['name']:
            existing_profile = profile

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if module.params['state'] == 'present':
        new_object = {
            'name': module.params['name'],
            'root_app_scope_id': existing_app_scope_id,
            'allow_broadcast': module.params['allow_broadcast'],
            'allow_link_local': module.params['allow_link_local'],
            'allow_multicast': module.params['allow_multicast'],
            'auto_upgrade_opt_out': module.params['auto_upgrade_opt_out'],
            'cpu_quota_mode': module.params['cpu_quota_mode'],
            'cpu_quota_pct': module.params['cpu_quota_pct'],
            'cpu_quota_us': module.params['cpu_quota_us'],
            'data_plane_disabled': module.params['data_plane_disabled'],
            'enable_dns': module.params['enable_dns'],
            'enable_forensics': module.params['enable_forensics'],
            'enable_meltdown': module.params['enable_meltdown'],
            'enable_pid_lookup': module.params['enable_pid_lookup'],
            'enforcement_cpu_quota_mode': module.params['enforcement_cpu_quota_mode'],
            'enforcement_cpu_quota_pct': module.params['enforcement_cpu_quota_pct'],
            'enforcement_cpu_quota_us': module.params['enforcement_cpu_quota_us'],
            'enforcement_disabled': module.params['enforcement_disabled'],
            'enforcement_max_rss_limit': module.params['enforcement_max_rss_limit'],
            'enforcement_max_rss_limit_mb': module.params['enforcement_max_rss_limit_mb'],
            'forensics_cpu_quota_mode': module.params['forensics_cpu_quota_mode'],
            'forensics_cpu_quota_pct': module.params['forensics_cpu_quota_pct'],
            'forensics_cpu_quota_us': module.params['forensics_cpu_quota_us'],
            'forensics_mem_quota_bytes': module.params['forensics_mem_quota_bytes'],
            'forensics_mem_quota_mb': module.params['forensics_mem_quota_mb'],
            'max_rss_limit': module.params['max_rss_limit'],
            'max_rss_limit_mb': module.params['max_rss_limit_mb'],
            'preserve_existing_rules': module.params['preserve_existing_rules'],
        }

        # Remove all the undefined parameters from the new_object
        new_object = {k: v for k, v in new_object.items() if v is not None}

        if existing_profile:
            if tet_module.is_subset(new_object, existing_profile):
                # If there is no change required to the module
                result['object'] = existing_profile
            else:
                # A change is required
                route = f"{TETRATION_API_AGENT_CONFIG_PROFILES}/{existing_profile['id']}"
                result['object'] = tet_module.run_method('PUT', route, req_payload=new_object)
                result['changed'] = True
        else:
            result['object'] = tet_module.run_method('POST', TETRATION_API_AGENT_CONFIG_PROFILES, req_payload=new_object)
            result['changed'] = True

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif module.params['state'] == 'absent':
        if existing_profile:
            route = f"{TETRATION_API_AGENT_CONFIG_PROFILES}/{existing_profile['id']}"
            result['object'] = tet_module.run_method('DELETE', route)
            result['changed'] = True
    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    else:
        if existing_profile:
            result['object'] = existing_profile

    module.exit_json(**result)


if __name__ == '__main__':
    main()
