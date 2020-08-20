import module_utils
import pytest
import json
#import requests

from module_utils import tetration
from module_utils import tetration_constants
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

from . import apikey


@pytest.fixture()
def api_info(api_key=apikey.API_KEY, api_secret=apikey.API_SECRET, endpoint=apikey.ENDPOINT):
    to_yield = {
        'api_key': api_key,
        'api_secret': api_secret,
        'endpoint': endpoint
    }
    yield to_yield


@pytest.fixture()
def rest_client(api_info):
    rest_client = tetration.RestClient(
        api_info['endpoint'],
        api_key=api_info['api_key'],
        api_secret=api_info['api_secret'],
        verify=True)

    yield rest_client


@pytest.fixture()
def tet_client(api_info):
    module_args = dict(
        first_name=dict(type='str', required=False, default=''),
        last_name=dict(type='str', required=False, default=''),
        provider=dict(
            type='dict', options=tetration_constants.TETRATION_PROVIDER_SPEC)
    )

    module_values = {
        'first_name': 'testfn',
        'last_name': 'testln',
        'provider': {
            'server_endpoint': api_info['endpoint'],
            'api_key': api_info['api_key'],
            'api_secret': api_info['api_secret'],
        }
    }
    set_module_args(module_values)

    module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True)

    yield tetration.TetrationApiModule(module)


@pytest.fixture()
def root_scope(rest_client):
    resp = rest_client.get(tetration_constants.TETRATION_API_SCOPES)

    assert len(resp.json()) > 0

    scope = resp.json()[0]
    yield scope['root_app_scope_id']


@pytest.fixture()
def test_user_id(rest_client, root_scope):
    req_payload = {
        "first_name": "Test",
        "last_name": "CICD User",
        "email": "test_user@test.com",
        "app_scope_id": root_scope
    }

    resp = rest_client.post(tetration_constants.TETRATION_API_USER,
                            json_body=json.dumps(req_payload))

    if resp.status_code == 200:
        # Create a new user
        created_user_id = resp.json()['id']
    elif resp.status_code in [400, 422]:
        # Reactivate the test user or the user is already active
        route = f"{tetration_constants.TETRATION_API_USER}?include_disabled=true"
        user_resp = rest_client.get(route)
        user_ids = [user['id']
                    for user in user_resp.json() if user['last_name'] == "CICD User"]
        if len(user_ids) != 1:
            print("Found more than one user")
            assert False
        if resp.status_code == 422:
            route = f"{tetration_constants.TETRATION_API_USER}/{user_ids[0]}/enable"
            enable_resp = rest_client.post(route)
            created_user_id = enable_resp.json()['id']
        elif resp.status_code == 400:
            created_user_id = user_ids[0]
        else:
            print(f'Found Unknown Status Code: {resp.status_code}')
            assert False
    else:
        # Got a status code other than what was defined above
        print(f"Got status code: {resp.status_code}")
        assert False

    yield created_user_id

    # Delete the created user
    user_route = f"{tetration_constants.TETRATION_API_USER}/{created_user_id}"
    # Look for any lingering roles and delete them

    resp = rest_client.get(user_route)

    roles = [role for role in resp.json()['role_ids']]
    for role in roles:
        route = f"{user_route}/remove_role"
        req_payload = {
            "role_id": role
        }
        resp = rest_client.delete(
            route, json_body=json.dumps(req_payload))
        assert resp.status_code == 200

    resp = rest_client.delete(user_route)

    assert resp.status_code == 200


def set_module_args(args):
    if '_ansible_remote_tmp' not in args:
        args['_ansible_remote_tmp'] = '/tmp'
    if '_ansible_keep_remote_files' not in args:
        args['_ansible_keep_remote_files'] = False

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class TestRestClient:
    def test_create_class_instance(self):
        server_endpoint = "https://www.google.com"
        rest_client_obj = tetration.RestClient
        obj = tetration.RestClient(server_endpoint)
        assert isinstance(obj, rest_client_obj)

    def test_rest_client_get_users(self, api_info):
        endpoint = api_info['endpoint']
        api_key = api_info['api_key']
        api_secret = api_info['api_secret']

        rest_client = tetration.RestClient(
            endpoint, api_key=api_key, api_secret=api_secret, verify=True)
        resp = rest_client.get(tetration_constants.TETRATION_API_USER)

        assert isinstance(resp.json(), list)
        assert resp.status_code == 200
        assert "openapi/v1/users" in str(resp.url)

    def test_rest_client_load_from_credentials_file(self, tmp_path, api_info):
        endpoint = api_info['endpoint']

        data = {
            'api_key': api_info['api_key'],
            'api_secret': api_info['api_secret']
        }

        d = tmp_path
        p = d / "test_creds.json"
        p.write_text(json.dumps(data))
        cred_file = str(p)

        rest_client = tetration.RestClient(
            endpoint, credentials_file=cred_file, verify=True)
        resp = rest_client.get(tetration_constants.TETRATION_API_USER)

        assert isinstance(resp.json(), list)
        assert resp.status_code == 200
        assert "openapi/v1/users" in str(resp.url)

    def test_add_remove_role_from_user(self, rest_client, test_user_id):
        user_route = f"{tetration_constants.TETRATION_API_USER}/{test_user_id}"
        role_route = f"{tetration_constants.TETRATION_API_ROLE}"

        resp = rest_client.get(user_route)
        resp_user = resp.json()

        # Get a list of all the roles in the system and pick the first one
        resp = rest_client.get(role_route)
        resp_roles = [role['id'] for role in resp.json() if role['id']
                      not in resp_user['role_ids']]

        assert len(resp_roles) > 0
        resp_role_id = resp_roles[0]

        # Add a role to a user
        req_payload = {
            "role_id": resp_role_id
        }

        route = f"{user_route}/add_role"
        resp = rest_client.put(route, json_body=json.dumps(req_payload))
        assert resp.status_code == 200

        # Verify the role has been added
        resp = rest_client.get(user_route)

        assert resp.status_code == 200
        assert resp_role_id in resp.json()['role_ids']

        # Remove the role
        route = f"{user_route}/remove_role"
        resp = rest_client.delete(route, json_body=json.dumps(req_payload))

        assert resp.status_code == 200
        assert resp_role_id not in resp.json()['role_ids']

    def test_read_invalid_credentials_file_missing_key(self, api_info, tmp_path):
        endpoint = api_info['endpoint']

        data = {}

        d = tmp_path
        p = d / "test_creds.json"
        p.write_text(json.dumps(data))
        cred_file = str(p)
        with pytest.raises(KeyError) as e:
            tetration.RestClient(
                endpoint, credentials_file=cred_file, verify=True)
        assert "api_key missing" in str(e.value)

    def test_read_invalid_credentials_file_missing_secret(self, api_info, tmp_path):
        endpoint = api_info['endpoint']

        data = {
            'api_key': api_info['api_key']
        }

        d = tmp_path
        p = d / "test_creds.json"
        p.write_text(json.dumps(data))
        cred_file = str(p)
        with pytest.raises(KeyError) as e:
            tetration.RestClient(
                endpoint, credentials_file=cred_file, verify=True)
        assert "api_secret missing" in str(e.value)

    def test_with_full_route_in_uri(self, rest_client):
        full_route = f'/openapi/v1{tetration_constants.TETRATION_API_USER}'
        resp = rest_client.get(full_route)
        users = resp.json()

        assert isinstance(rest_client, tetration.RestClient)
        assert isinstance(users, list)

    def test_send_invalid_http_method(self, rest_client):
        resp = rest_client.signed_http_request(
            "HEAD", tetration_constants.TETRATION_API_USER)

        assert resp is None

    def test_api_key_is_empty(self, api_info, tmp_path):
        endpoint = api_info['endpoint']

        data = {
            'api_key': '',
            'api_secret': ''
        }

        d = tmp_path
        p = d / "test_creds.json"
        p.write_text(json.dumps(data))
        cred_file = str(p)
        rest_client = tetration.RestClient(
            endpoint, credentials_file=cred_file, verify=True)
        resp = rest_client.get(tetration_constants.TETRATION_API_USER)

        assert resp is None

    def test_api_secret_is_empty(self, api_info, tmp_path):
        endpoint = api_info['endpoint']

        data = {
            'api_key': 'fakekey',
            'api_secret': ''
        }

        d = tmp_path
        p = d / "test_creds.json"
        p.write_text(json.dumps(data))
        cred_file = str(p)
        rest_client = tetration.RestClient(
            endpoint, credentials_file=cred_file, verify=True)
        resp = rest_client.get(tetration_constants.TETRATION_API_USER)

        assert resp is None


class TestMultiPartOption:
    def test_create_multi_part_option_class_instance(self):
        test_key = "key"
        test_value = "value"

        mpo_obj = tetration.MultiPartOption
        obj = tetration.MultiPartOption(test_key, test_value)

        assert isinstance(obj, mpo_obj)

    def test_multi_part_option_object_data(self):
        test_key = "key"
        test_value = "value"

        obj = tetration.MultiPartOption(test_key, test_value)

        assert hasattr(obj, "key")
        assert hasattr(obj, "val")
        assert obj.key == test_key
        assert obj.val == test_value


class TestTetrationApiModule:
    def test_create_class_instance_missing_parameters(self):
        module_args = dict(
            name=dict(type='str', required=True),
            email=dict(type='bool', required=False, default=False)
        )

        module_values = {
            'name': 'testname',
            'email': False
        }
        set_module_args(module_values)

        module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True)

        with pytest.raises(SystemExit) as e:
            tetration.TetrationApiModule(module)

        assert str(e.value) == '1'

    def test_obj_add_fake_key(self):
        # Creates a new object (deep copy)
        fake_options = {
            k: v for k, v in tetration_constants.TETRATION_PROVIDER_SPEC.items()}
        fake_options['fake_key'] = dict(type='str', default='fake')

        module_args = dict(
            first_name=dict(type='str', required=False, default=''),
            last_name=dict(type='str', required=False, default=''),
            provider=dict(
                type='dict', options=fake_options)
        )

        module_values = {
            'first_name': 'testfn',
            'last_name': 'testln',
            'provider': {
                'server_endpoint': 'https://fake.com',
                'api_key': 'deadbeef',
                'api_secret': 'beef',
                'fake_key': 'fake_value'
            }
        }
        set_module_args(module_values)

        module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True)

        tet_module = tetration.TetrationApiModule(module)

        # Need to mock RestClient and assert the values it was called with   #TODO
        assert isinstance(tet_module, tetration.TetrationApiModule)

    def test_obj_missing_required_key_with_default_value(self):
        # Creates a new object (deep copy)
        fake_options = {
            k: v for k, v in tetration_constants.TETRATION_PROVIDER_SPEC.items()}
        fake_options.pop('verify')

        module_args = dict(
            first_name=dict(type='str', required=False, default=''),
            last_name=dict(type='str', required=False, default=''),
            provider=dict(
                type='dict', options=fake_options)
        )

        module_values = {
            'first_name': 'testfn',
            'last_name': 'testln',
            'provider': {
                'server_endpoint': 'https://fake.com',
                'api_key': 'deadbeef',
                'api_secret': 'beef'
            }
        }
        set_module_args(module_values)

        module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True)

        tet_module = tetration.TetrationApiModule(module)

        # Need to mock RestClient and assert the values it was called with  #TODO
        assert isinstance(tet_module, tetration.TetrationApiModule)

    def test_obj_get_users(self, tet_client):
        tet_resp = tet_client.get('/users')
        print(tet_resp)

        assert False
