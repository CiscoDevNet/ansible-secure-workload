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
module: tetration_software_agent

short_description: Queries and deletes software agents by uuid

version_added: '2.8'

description:
- Enables query or removal of software agents by uuid
- Searching by C(uuid) returns all parameters from the API
- Marking as absent deletes the 

notes:
- Supports check mode.
options:
  uuid:
    description: UUID of target agent
    type: string
    required: true
  state:
    choices: [absent, query]
    default: query
    description: Remove or query for software agent
    required: true
    type: string

extends_documentation_fragment: tetration_doc_common

author: 
  - Brandon Beck (@techbeck03)
  - Joe Jacobs(@joej164)
'''

EXAMPLES = '''
# Remove agent by uuid
tetration_software_agent:
    uuid: 4b35fa6001339e5313af5e34bd88012381a9aaaa
    state: absent
    provider:
      host: "https://tetration-cluster.company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query agent by hostname
tetration_software_agent:
    uuid: 4b35fa6001339e5313af5e34bd88012381a9aaaa
    state: query
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = '''
---
object:
  contains:
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
      returned: when C(state) is present or query
      sample: d322189839fb70b2f4569f3657eea58f096c0686
      type: int
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.tetration_constants import TETRATION_PROVIDER_SPEC
from ansible.module_utils.tetration_constants import TETRATION_API_SENSORS
from ansible.module_utils.tetration import TetrationApiModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        uuid=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=['absent', 'query']),
        provider=dict(type='dict', options=TETRATION_PROVIDER_SPEC)
    )

    # Create the return object
    result = {
        'object': None,
        'changed': False
    }

    module = AnsibleModule(
        argument_spec=module_args
    )

    tet_module = TetrationApiModule(module)

    response = None
    route = f"{TETRATION_API_SENSORS}/{module.params['uuid']}"
    if module.params['state'] == 'query':
        response = tet_module.run_method('GET', route)
    elif module.params['state'] == 'absent':
        response = tet_module.run_method('DELETE', route)
        result['changed'] == True

    result['object'] = response

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
