#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tetration_software_agent_query

short_description: Allows for searching software agents based on desired filters 

version_added: '2.8'

description:
- Enables searching for software agents based on a number of preconfigured filters
- Returns a list of matching software agents based on the passed in criteria

notes:
- This module only queries.  Use M(tetration_software_agent) to delete or query an agent by UUID
- If you don't provide any parameters, will return all agents in the system

options:
  host_name_contains:
    description: Searches for all software agents whos name includes the string
    type: string
  host_name_is_exactly:
    description: Searches for all software agents whos name matches exactly 
    type: string

extends_documentation_fragment: tetration_doc_common

author: 
  - Brandon Beck (@techbeck03)
  - Joe Jacobs(@joej164)
'''

EXAMPLES = '''
# Find an agent by exact name 
tetration_software_agent_query:
    host_name_is_exactly: student-867-0
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Find an agent whos name contains a string 
tetration_software_agent_query:
    host_name_contains: student
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Find all agents 
tetration_software_agent_query:
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

'''

RETURN = '''
---
object:
  contains: [
    agent_type:
      description: Agent type
      sample: ENFORCER
      type: string
    arch:
      description: CPU architecture type
      sample: x86_64
      type: string
    auto_upgrade_opt_out:
      description: If True, agents are not auto-upgraded during upgrade of Tetration
        cluster
      sample: 'False'
      type: bool
    cpu_quota_mode:
      description: The amount of CPU quota to give to agent on the end host (pct)
      sample: 1
      type: int
    cpu_quota_us:
      description: The amount of CPU quota to give to agent on the end host (us)
      sample: 30000
      type: int
    created_at:
      description: Date this inventory was created (Unix Epoch)
      sample: 1553626033
      type: string
    current_sw_version:
      description: Current version of software agent
      sample: 3.1.1.65-enforcer
      type: string
    data_plane_disabled:
      description: If true, agent stops reporting flows to Tetration
      sample: 'False'
      type: bool
    desired_sw_version:
      description: Desired version of software agent
      sample: 3.1.1.65-enforcer
      type: string
    enable_cache_sidechannel:
      description: Whether or not sidechannel detection is enabled
      sample: 'True'
      type: bool
    enable_forensic:
      description: Whether or not forensics is enabled
      sample: 'True'
      type: bool
    enable_meltdown:
      description: Whether or not meltdown detection is enabled
      sample: 'True'
      type: bool
    enable_pid_lookup:
      description: Whether or not pid lookup for flow search is enabled
      sample: 'True'
      type: bool
    host_name:
      description: Hostname as reported by software agent
      returned: when C(state) is present or query
      sample: acme-example-host
      type: string
    interfaces:
      description: List of interfaces reported by software agent
      sample: JSON Interfaces
      type: list
    last_config_fetch_at:
      description: Date of last configuration fetch (Unix Epoch)
      sample: 1563458124
      type: string
    last_software_update_at:
      description: Date of last software update (Unix Epoch)
      sample: 1553626033
      type: string
    platform:
      description: OS platform type
      sample: CentOS-7.6
      type: string
    uuid:
      description: UUID of the registered software agent
      returned: when matching value found 
      sample: d322189839fb70b2f4569f3657eea58f096c0686
      type: int
  ]
  description: the changed or modified object(s)
  returned: always
  type: list
'''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration_constants import TETRATION_API_SENSORS
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        host_name_contains=dict(type='str'),
        host_name_is_exactly=dict(type='str'),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # Create the return object
    result = {
        'object': [],
        'changed': False
    }

    module = AnsibleModule(
        argument_spec=module_args
    )

    tet_module = TetrationApiModule(module)

    response = tet_module.run_method('GET', TETRATION_API_SENSORS)

    for s in response['results']:
        if 'deleted_at' not in s.keys():
            to_append = s

            if module.params['host_name_contains'] and module.params['host_name_contains'] not in s['host_name']:
                to_append = None
            if module.params['host_name_is_exactly'] and module.params['host_name_is_exactly'] != s['host_name']:
                to_append = None

            if to_append is not None:
                result['object'].append(to_append)

    result['items_found'] = len(result['object'])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
