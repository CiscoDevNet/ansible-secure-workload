Secure Workload (Tetration) Ansible Module
=========

An ansible role for administrating Secure Workload (formerly known as Tetration). Find a guided walkthourgh of the [Ansible modules here](https://developer.cisco.com/learning/tracks/cisco-app-first-security/cisco-secure-workload-ansible/ansible-intro/step/1).

Requirements
------------

- Python 3.7 or later
- Ansible 2.9 and later
- Python `requests` package must be installed on the server.
- API Key with the following permissions
  - app_policy_management
  - sensor_management
  - user_data_upload
  - user_role_scope_management

Role Variables
--------------

The following variables need to be explicitly imported in to the role OR can be set as environmental variables.
  - TETRATION_SERVER_ENDPOINT
  - TETRATION_API_KEY
  - TETRATION_API_SECRET

The api key and secret can be obtained from the **Settings -> API Keys** menu in Tetration.

The server endpoint is just the base URL of your Tetration, e.g. "https://acme.tetrationcloud.com".

Dependencies
------------

`requests`

This role uses the Python `requests` package to communicate via https with Tetration.

Example Playbook
----------------
```
    - name: Add User to Tetration 
      hosts: localhost
      connection: local
      roles:
        - role: ansible-module 
    
      tasks:
        - name: read variables from the environment to be explicit
          set_fact:
            ansible_host: "{{ lookup('env', 'TETRATION_SERVER_ENDPOINT') }}"
            api_key: "{{ lookup('env', 'TETRATION_API_KEY') }}"
            api_secret: "{{ lookup('env', 'TETRATION_API_SECRET') }}"
          no_log: True 
    
        - name: put the variables in the required format
          set_fact:
            provider_info:
              api_key: "{{ api_key }}"
              api_secret: "{{ api_secret }}"
              server_endpoint: "{{ ansible_host }}"
          no_log: True
    
        - name: Create or verify a test user exists in the system
          tetration_user:
            provider: "{{ provider_info }}"
            email: test_user@test.com
            first_name: "Test"
            last_name: "User"
            app_scope_name: "RootScope"
            role_names:
              - Execute
              - Enforce
            state: present 
          delegate_to: localhost
          register: output
```

Testing
-------
Python Testing is done via Pytest.
- Create a Virtual Environment
- Install Dependencies from `requirements.txt`
- Run the command `pytest --cov=. --cov-report term-missing --cov-fail-under=80 tests/`

Ansible Testing is done via Molecule
- Create a Virtual Environment
- Install Dependencies from `requirements.txt`
- Run the command `molecule test -s tetration_user` to run the users scenario (check the `molecule` directory for all scenarios)
- Run the command `molecule test --all` to run all the scenarios

The scenarios are in the **molecule** folder.  Each scenario is named after the module its tests are written for.  Molecule is designed to do stuff to a VM/Container and then test the state of the container.  Since this is not the case, instead we use the `converge.yml` file to exercise the role.  

Environmental variables are set in the `molecule.yml` file.  If you have an `.env.yml` file set in the project root, when molecule runs, it will set the contents of that file as environmental variables. This way you can test both local and remote.

Installing From GitHub
----------------------
This is the process to install this role directly from GitHub into ansible

- Install Ansible (ideally in a python virtual environment).  The commands for linux are below
  - `python3 -m venv venv`
  - `source venv/bin/activate`
  - `pip install --upgrade pip`
  - `pip install 'ansible==2.9.13'`
  - `pip install requests`
- If the Repo is Private, create a Personal Access Token or be prepared to enter your username and password into Ansible Galaxy
- Clone the repo using `ansible-galaxy`
  - `ansible-galaxy install git+https://<your github userid>:<your github token>@github.com/tetration-exchange/ansible-module.git`
- Set environmental variables required for the sample plays to run
  - TETRATION_SERVER_ENDPOINT
  - TETRATION_API_KEY
  - TETRATION_API_SECRET
- Use the modules in plays
  - See the examples folder for an example of using the module when installed from Galaxy

Storing Environmental Variables in a File
-----------------------------------------
An option to setting an environmental variable is to use `dotenv` to load them at run time.  You can create a `.env` file that can be excluded from source control.  This section covers how to install and use it.

- An option to using environmental variables is you can install python dotenv
  - `pip install "python-dotenv[cli]"`
- Then you can put the environmental variables into a file called `.env` at the root of the repo that looks like

.env
```
TETRATION_API_KEY="my api key"
TETRATION_API_SECRET="my apy password"
TETRATION_SERVER_ENDPOINT="https://acme.tetrationcloud.com"
```
- Run the sample plays as follows
  - `dotenv run ansible-playbook sample_play.yml`

Running the Module locally
--------------------------
If you want to work on the module in a local environment, you'll need to create an `ansible.cfg` file with the following contents:

ansible.cfg
```
[defaults]

# Tetration modules
library = ./
module_utils = ./module_utils
doc_fragment_plugins = ./plugins/doc_fragments

# Helps read debug outputs better
stdout_callback = debug
```

License
-------

MIT


Author Information
------------------

Cisco

This module is provided as-is with community support only.
