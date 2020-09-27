import pytest
import json

from module_utils import tetration
from module_utils import tetration_constants
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

from dotenv import load_dotenv
import os


@pytest.fixture()
def api_info():
    # This allows you to put all the environmental variables into a `.env`
    # file in the repo and will take the contents of the file and push them
    # into the OS environmental variables.
    # This allows for testing locally and with github actions
    load_dotenv()
    api_key = os.getenv("TETRATION_API_KEY")
    api_secret = os.getenv("TETRATION_API_SECRET")
    endpoint = os.getenv("TETRATION_SERVER_ENDPOINT")

    if not all([api_key, api_secret, endpoint]):
        assert False

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
                    for user in user_resp.json() if user['email'] == "test_user@test.com"]
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

    # ###Delete the created user

    # Look for any lingering roles and delete them
    user_route = f"{tetration_constants.TETRATION_API_USER}/{created_user_id}"

    resp = rest_client.get(user_route)
    if resp.status_code == 404:
        # If the user was disabled during testing, reenable for cleanup
        enable_route = f"{user_route}/enable"
        resp = rest_client.post(enable_route)

    roles = [role for role in resp.json()['role_ids']]
    for role in roles:
        route = f"{user_route}/remove_role"
        req_payload = {
            "role_id": role
        }
        resp = rest_client.delete(
            route, json_body=json.dumps(req_payload))
        assert resp.status_code == 200

    resp = rest_client.put(user_route, json_body=json.dumps(req_payload))
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
    def test_create_class_instance_missing_parameters(self, monkeypatch):
        # The environment variables were bleeding over from other tests
        # Ensures at least one required variable is missing for this test
        monkeypatch.delenv("TETRATION_API_KEY", raising=False)
        module_args = dict(
            name=dict(type='str', required=True),
            email=dict(type='bool', required=False, default=False)
        )

        module_values = {
            'name': 'some name',
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
        tet_resp = tet_client.run_method(
            'GET', tetration_constants.TETRATION_API_USER)

        assert isinstance(tet_resp, list)
        assert len(tet_resp) > 0

    def test_obj_get_sensors_paginated(self, tet_client):
        tetration_constants.TETRATION_API_PAGINATION_SIZE = 10

        tet_resp = tet_client.run_method_paginated(
            'GET', tetration_constants.TETRATION_API_SENSORS)
        assert isinstance(tet_resp, list)
        assert len(tet_resp) > 0

    def test_obj_get_all_users_including_disabled_using_parameter(self, tet_client):
        params = {'include_disabled': True}
        tet_resp = tet_client.run_method(
            'GET', tetration_constants.TETRATION_API_USER, params=params)

        assert isinstance(tet_resp, list)
        assert len(tet_resp) > 0
        disabled_users = [user for user in tet_resp if not user['disabled_at']]
        assert len(disabled_users) > 0

    def test_obj_get_invalid_route(self, tet_client):
        with pytest.raises(SystemExit):
            tet_client.run_method('GET', '/fakeroute')

    def test_obj_get_invalid_user(self, tet_client):
        fake_user_id = '123456'
        route = f"{tetration_constants.TETRATION_API_USER}/{fake_user_id}"
        with pytest.raises(SystemExit):
            tet_client.run_method('GET', route)

    def test_obj_update_last_name(self, tet_client, test_user_id):
        route = f"{tetration_constants.TETRATION_API_USER}/{test_user_id}"

        req_payload = {
            "last_name": "Test User",
        }

        resp = tet_client.run_method('PUT', route, req_payload=req_payload)
        resp = tet_client.run_method('GET', route)

        assert resp['last_name'] == req_payload['last_name']

    def test_obj_delete_enable_user(self, tet_client, test_user_id):
        route = f"{tetration_constants.TETRATION_API_USER}/{test_user_id}"
        enable_route = f"{route}/enable"

        # Get the user info, verify initial state
        resp = tet_client.run_method('GET', route)
        assert resp['disabled_at'] is None

        # Mark the user as deleted, get the info and confirm change
        resp = tet_client.run_method('DELETE', route)
        assert resp['disabled_at'] is not None

        # Mark the user as enabled, get the info and confirm change
        resp = tet_client.run_method('POST', enable_route)
        resp = tet_client.run_method('GET', route)
        assert resp['disabled_at'] is None

    def test_obj_enable_fake_user(self, tet_client):
        fake_user_id = '123456'
        enable_route = f"{tetration_constants.TETRATION_API_USER}/{fake_user_id}/enable"

        with pytest.raises(SystemExit):
            tet_client.run_method('POST', enable_route)

    def test_obj_update_last_name_invalid_user(self, tet_client):
        fake_user = '123456'
        route = f"{tetration_constants.TETRATION_API_USER}/{fake_user}"

        req_payload = {
            "last_name": "Test User",
        }

        with pytest.raises(SystemExit):
            tet_client.run_method('PUT', route, req_payload=req_payload)

    def test_obj_delete_invalid_user(self, tet_client):
        fake_user = '123456'
        route = f"{tetration_constants.TETRATION_API_USER}/{fake_user}"

        with pytest.raises(SystemExit):
            tet_client.run_method('DELETE', route)

    def test_get_object_with_passed_in_object(self, tet_client, test_user_id):
        resp = tet_client.run_method(
            'GET', tetration_constants.TETRATION_API_USER)

        filter = dict(
            id=test_user_id
        )

        filtered_resp = tet_client.get_object(filter, search_array=resp)

        assert filtered_resp['id'] == test_user_id

    def test_get_object_from_server_filter_by_last_name(self, tet_client, test_user_id):
        route = f"{tetration_constants.TETRATION_API_USER}/{test_user_id}"

        resp = tet_client.run_method('GET', route)

        filter = dict(
            last_name=resp['last_name']
        )

        filtered_resp = tet_client.get_object(
            filter, target=tetration_constants.TETRATION_API_USER)

        assert filtered_resp['id'] == test_user_id

    def test_get_object_from_server_filter_by_last_name_allow_multiple(self, tet_client, test_user_id):
        route = f"{tetration_constants.TETRATION_API_USER}/{test_user_id}"

        resp = tet_client.run_method('GET', route)

        filter = dict(
            last_name=resp['last_name']
        )

        filtered_resp = tet_client.get_object(
            filter,
            target=tetration_constants.TETRATION_API_USER,
            allow_multiple=True)

        assert isinstance(filtered_resp, list)
        assert filtered_resp[0]['id'] == test_user_id

    def test_is_subset_both_match_check_only(self, tet_client):
        test_obj1 = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)

        assert resp is True

    def test_is_subset_different_objects_check_only(self, tet_client):
        test_obj1 = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        test_obj2 = {
            'a': 1,
            'b': 3,
            'c': 2
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)

        assert resp is False

    def test_is_subset_obj1_smaller(self, tet_client):
        test_obj1 = {
            'a': 1,
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)

        assert resp is True

    def test_is_subset_obj_2_bigger(self, tet_client):
        test_obj1 = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)

        assert resp is False

    def test_is_subset_obj1_not_in_obj2(self, tet_client):
        test_obj1 = {
            'd': 1,
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)

        assert resp is False

    def test_is_subset_obj_2_deeply_nested(self, tet_client):
        test_obj1 = {
            'd': 1,
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': False,
            'd': {
                'e': [4, 5, 6],
                'f': {
                    'g': 7
                }
            }
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)

        assert resp is False

    def test_is_subset_object_same_with_lists(self, tet_client):
        test_obj1 = {
            'a': 1,
            'b': 2,
            'c': [3, 4, 5]
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': [3, 4, 5]
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)
        assert resp is True

    def test_is_subset_same_keys_with_different_lists(self, tet_client):
        test_obj1 = {
            'a': 1,
            'b': 2,
            'c': [3, 4, 5]
        }

        test_obj2 = {
            'a': 1,
            'b': 2,
            'c': [3, 4, 5, 6]
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)
        assert resp is False

    def test_is_subset_with_completly_different_objects(self, tet_client):
        test_obj1 = {
            'a': 1,
            'b': 2,
            'c': [3, 4, 5]
        }

        test_obj2 = {
            'd': 1,
            'e': 2,
            'f': [3, 4, 5, 6]
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)
        assert resp is False

    def test_is_subset_same_with_same_sub_dicts(self, tet_client):
        test_obj1 = {
            'a': {
                'b': 2,
                'c': 3
            },
            'd': 4
        }
        test_obj2 = {
            'a': {
                'b': 2,
                'c': 3
            },
            'd': 4
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)
        assert resp is True

    def test_is_subset_same_with_different_sub_dicts(self, tet_client):
        test_obj1 = {
            'a': {
                'b': 2,
                'c': 3
            },
            'd': 4
        }
        test_obj2 = {
            'a': {
                'b': 2,
                'c': 4
            },
            'd': 4
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)
        assert resp is False

    def test_is_subset_same_with_nested_same_smaller_object(self, tet_client):
        test_obj1 = {
            'a': {
                'b': 2,
                'c': [3, 4, {'a': 1, 'b': 2}]
            }
        }
        test_obj2 = {
            'a': {
                'b': 2,
                'c': [3, 4, {'a': 1, 'b': 2}]
            },
            'd': 4
        }

        resp = tet_client.is_subset(test_obj1, test_obj2)
        assert resp is True

    def test_is_subset_with_same_lists(self, tet_client):
        test_obj1 = [1, 2, 3]
        test_obj2 = [1, 2, 3]

        with pytest.raises(TypeError) as e:
            tet_client.is_subset(test_obj1, test_obj2)

        assert str(e.value) == "Both objects must be dictionaries."
