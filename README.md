Role Name
=========

A brief description of the role goes here.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

Testing
-------
Python Testing is done via Pytest.
- Create a Virtual Environment
- Install Dependencies from `requirements.txt`
- Run the command `pytest --cov=. --cov-report term-missing --cov-fail-under=80 tests/`

Ansible Testing is done via Molecule
- Create a Virtual Environment
- Install Dependencies from `requirements.txt`
- Run the command `molecule converge -s users` to run the Users scenario
- Run the command `molecule converge --all` to run all the scenarios

The scenarios are in the **molecule** folder.  Each scenario is named after the module its tests are written for.  Molecule is designed to do stuff to a VM/Container and then test the state of the container.  Since this is not the case, instead we use the `converge.yml` file to exercize the role.  

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
TETRATION_SERVER_ENDPOINT="https://ignwpov.tetrationpreview.com"
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

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
