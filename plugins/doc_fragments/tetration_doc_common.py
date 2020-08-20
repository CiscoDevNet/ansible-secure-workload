class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = """
options:
  provider:
    description:
      - A dict object containing connection details.
    suboptions:
      server_endpoint:
        description:
          - Specifies the DNS host name or address for connecting to the remote
            tetration cluster
          - Value can also be specified using C(TETRATION_SERVER_ENDPOINT) environment
            variable.
        required: true
      api_key:
        description:
          - API Key used for tetration authentication
          - Value can also be specified using C(TETRATION_API_KEY) environment
            variable.
        required: true
      api_secret:
        description:
          - Specifies the API secret used for tetration authentication
          - Value can also be specified using C(TETRATION_API_SECRET) environment
            variable.
        required: true
      verify:
        description:
          - Boolean value to enable or disable verifying SSL certificates
          - Value can also be specified using C(TETRATION_VERIFY) environment
            variable.
        type: bool
        default: 'no'
      timeout:
        description:
          - The amount of time before to wait before receiving a response
          - Value can also be specified using C(TETRATION_TIMEOUT) environment
            variable.
        default: 10
      max_retries:
        description:
          - Configures the number of attempted retries before the connection
            is declared usable
          - Value can also be specified using C(TETRATION_MAX_RETRIES) environment
            variable.
        type: int
        default: 3
      api_version:
        description:
          - Specifies the version of Tetration OpenAPI to use
          - Value can also be specified using C(TETRATION_API_VERSION) environment
            variable.
        type: str
        default: v1
notes:
  - "This module must be run locally, which can be achieved by specifying C(connection: local)."
  - Please read the :ref:`tetration_guide` for more detailed information on how to use Tetration with Ansible.

"""
