Cisco Secure Workload (formerly Tetration) Asnible Module
=====================================

Ansible’s simple automation framework paired with Cisco’s architectures and programmable platforms provide the optimal combination for open network automation. Cisco DevNet provides Ansible modules, use-case focused content, and Learning Labs to successfully deploy automation and implement DevOps into your network operations.

Ansible is a Deployment, Orchestration, and Configuration Management tool that is well known for its ease of use. It is open source, simple to work with and powerful enough to help automate complex solutions. It’s goal is to provide productivity gains to a wide variety of automation challenges.

One of the largest benefits of Ansible versus other configuration control software is that Ansible has no agent. This allows Ansible to be extremely lightweight compared to its competitors. Ansible works by having access to the end devices (usually through SSH or API calls) and executing a series of instructions on those devices through a range of methods, but commonly through the python programming language.

The Secure Workload Ansible module allows you to:

* Control Cisco Secure Workload (Tetration) with Ansible using the `tetration_user` module to add, remove and validate Tetration users.
* Add, remove and modify Scopes in Tetration using the `tetration_scope_query`, `tetration_scope`, and the `tetration_scope_commit_query_changes`.
* Add, remove and modify Tetration `roles` using the `tetration_role` module. 
* Remove agents or decommission workloads using the `tetration_software_agent` and `tetration_software_agent_query`.   
* Use the `tetration_software_agent` and `tetration_software_agent_query` modules to validate that an agent successfully installed and verify that workload has been registered to the Tetration manager.

## Related Sandbox
* [Cisco Secure Workload Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/e95caf39-0b4a-45da-9305-49a65f8dce97?diagramType=Topology)
* [Cisco Application-First Security Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/88e9fabf-abbf-4c0b-b1a1-c4999d794a10?diagramType=Topology)

## Links to DevNet Learning Labs
* [Cisco Secure Workload introduction labs](https://developer.cisco.com/learning/modules/secure-workload/Tetration-Intro-APIs-Learning-Lab/step/1)
* [Cisco Application-First Security labs](https://developer.cisco.com/learning/modules/cisco-app-first-security-lab/app-first-sec-aws-lab/step/1)
