import os
import json
import requests
import hmac
import hashlib
import base64
import time
import warnings

from datetime import datetime
from six.moves.urllib.parse import urljoin
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_text
from . import tetration_constants
from requests.packages.urllib3 import disable_warnings

# Disable SSL Warnings
disable_warnings()


class TetrationApiBase(object):
    ''' Base class for implementing Tetration API '''
    provider_spec = {'provider': dict(
        type='dict', options=tetration_constants.TETRATION_PROVIDER_SPEC)}

    def __init__(self, provider, module):
        if len(provider.keys()) > 0:
            to_del = []
            for key in provider.keys():
                if key not in tetration_constants.TETRATION_PROVIDER_SPEC.keys():
                    to_del.append(key)
            for key in to_del:
                provider.pop(key)
        for key, value in iteritems(tetration_constants.TETRATION_PROVIDER_SPEC):
            if key not in provider:
                # apply default values from NIOS_PROVIDER_SPEC since we cannot just
                # assume the provider values are coming from AnsibleModule
                if 'default' in value:
                    provider[key] = value['default']
                # override any values with env variables unless they were
                # explicitly set
                env = ('TETRATION_%s' % key).upper()
                if env in os.environ:
                    provider[key] = os.environ.get(env)
                # if key is required but still not defined raise Exception
                if key not in provider and 'required' in value and value['required']:
                    raise ValueError('option: %s is required' % key)
        self.rc = RestClient(**provider)


class TetrationApiModule(TetrationApiBase):
    ''' Implements Tetration OpenAPI for executing a tetration module '''

    def __init__(self, module):
        self.module = module
        provider = module.params.get(
            'provider') if module.params.get('provider') else dict()
        try:
            super(TetrationApiModule, self).__init__(provider, module)
        except Exception as exc:
            self.module.fail_json(msg=to_text(exc))

    def _handle_exception(self, method_name, exc):
        ''' Handles any exceptions raised
        This method is called when an unexpected response
        code is returned from a Tetration OpenAPI call
        '''
        self.module.fail_json(
            msg=exc.text,
            code=exc.status_code,
            operation=method_name
        )

    def get_object(self, filter, target=None, params=None, sub_element=None, allow_multiple=False, search_array=None):
        '''Returns a single object from Tetration that exactly matches every
        value specified in filter.
        '''
        result_array = []
        while True:
            if search_array:
                query_result = search_array
            else:
                query_result = self._get(
                    target=target, params=params, req_payload=None)
            search_objects = query_result[sub_element] if sub_element and sub_element in query_result else query_result
            for obj in search_objects:
                match = True
                for k, v in iteritems(filter):
                    if k in obj and obj[k] != v:
                        match = False
                if match:
                    if allow_multiple:
                        result_array.append(obj)
                    else:
                        return obj
            if 'offset' in query_result and not search_array:
                params['offset'] = query_result['offset']
            else:
                return result_array if result_array else None

    def run_method(self, method_name, target, params=None, req_payload=None):
        methods = {
            'get': self._get,
            'post': self._post,
            'put': self._put,
            'delete': self._delete
        }
        return methods[method_name.lower()](target, params, req_payload)

    def run_method_paginated(self, method_name, target, params=None, req_payload=None, offset=None):
        methods = {
            'get': self._get,
            'post': self._post,
            'put': self._put,
            'delete': self._delete
        }
        if params is None:
            params = {
                'limit': tetration_constants.TETRATION_API_PAGINATION_SIZE,
                'offset': offset
            }
        else:
            params['limit'] = tetration_constants.TETRATION_API_PAGINATION_SIZE
            params['offset'] = offset

        keep_searching = True
        all_results = []
        while keep_searching:
            results = methods[method_name.lower()](target, params, req_payload)

            all_results.extend(results['results'])
            if 'offset' in results.keys():
                params['offset'] = results['offset']
            else:
                keep_searching = False

        return all_results

    def _get(self, target, params, req_payload):
        resp = self.rc.get(target, params=params)
        if resp.status_code == 400:
            return None
        elif resp.status_code == 200:
            return resp.json()
        else:
            self._handle_exception('get', resp)

    def _post(self, target, params, req_payload):
        resp = self.rc.post(target, json_body=json.dumps(req_payload))
        if resp.status_code in tetration_constants.TETRATION_API_SUCCESS_CODES:
            try:
                return resp.json()
            except ValueError:
                return None
        else:
            self._handle_exception('post', resp)

    def _put(self, target, params, req_payload):
        resp = self.rc.put(target, json_body=json.dumps(req_payload))
        if resp.status_code in tetration_constants.TETRATION_API_SUCCESS_CODES:
            try:
                return resp.json()
            except ValueError:
                return None
        else:
            self._handle_exception('put', resp)

    def _delete(self, target, params, req_payload):
        resp = self.rc.delete(target, json_body=json.dumps(req_payload))
        if resp.status_code in tetration_constants.TETRATION_API_SUCCESS_CODES:
            try:
                return resp.json()
            except ValueError:
                return None
        elif resp.status_code in tetration_constants.TETRATION_API_FAILURE_CODES_THAT_RETURN_DATA:
            try:
                return resp.json()
            except ValueError:
                return None
        else:
            self._handle_exception('delete', resp)

    def is_subset(self, smaller_obj, bigger_obj):
        # Accepts 2 dictionaries and determines if the first dict is a subset of the second dict
        if not isinstance(smaller_obj, dict) or not isinstance(bigger_obj, dict):
            raise TypeError("Both objects must be dictionaries.")

        for k, v in smaller_obj.items():
            if bigger_obj.get(k) != v:
                return False
        return True


class MultiPartOption(object):
    """
    Key/value pair in the MultiPart body
    """

    def __init__(self, key, val):
        self.key = key
        self.val = val


class RestClient(object):
    """
    A high-level client class for communication with Tetration API server.
    Provides query requests.

    Attributes:
        server_endpoint: String of server URL to query
        uri_prefix: String prefix of URI Path
        api_key: String of hex API key provided by Tetration key generation UI.
        api_secret: String of hex API secret provided by Tetration key
        generation UI.
        verify: Boolean for SSL verification of requests.
        session: requests.Session object to execute requests

    Constants:
        SUPPORTED_METHODS: list of supported HTTP methods
    """
    __MULTIPART_BOUNDARY_ID = 'CiscoTetrationClient'
    __MULTIPART_FILE_ID = 'file'
    __DEFAULT_MAX_RETRIES = 3
    __DEFAULT_TIMEOUT = 10
    __RETRY_HTTP_CODES = [429, 502, 503, 504]
    __RETRY_METHODS = ['GET', 'PUT', 'DELETE']
    __SLEEP_BETWEEN_RETRIES_SEC = 2

    SUPPORTED_METHODS = ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']

    def __init__(self, server_endpoint, **kwargs):
        """
        Init begins a persistent requests.Session and can be accessed by
        attribute RestClient.session.

        Example use case:
        rc = RestClient("https://example-server-endpoint.com",
                        credentials_file="~/.tetration/credentials.json",
                        verify=False) # disable SSL certification verification

        Format of credentials.json:
        {
                "api_key": "<hex string>",
                "api_secret": "<hex string>"
        }

        Args:
            server_endpoint: String of the server URL to query generation UI.
            kwargs:
                ___NOTE___: for production scripts, it is a good idea to pass
                credentials in a file using credentials_file option.
                Passing api_key and api_secret to the constructor is meant for
                quick development and prototyping. Putting credentials in the
                scripts is dangerous as credentials can get checked into code
                repository.

                api_version: API Version.
                verify: Boolean to verify SSL cerfications.
                credentials_file: JSON file containing api_key and api_secret.
                api_key: String of hex API key provided by Tetration UI.
                api_secret: String of hex API secret provided by Tetration UI.
                max_retries: int for max retries for requests
        """
        self.server_endpoint = server_endpoint
        self.uri_prefix = '/openapi/' + kwargs.get('api_version', 'v1')
        self.credentials_file = kwargs.get('credentials_file', None)
        if self.credentials_file is not None:
            self.__load_credentials_from_file()
        else:
            self.api_key = kwargs.get('api_key', '').encode('ascii')
            self.api_secret = kwargs.get('api_secret', '').encode('ascii')
        self.verify = kwargs.get('verify', True)
        self.session = requests.Session()
        self.retries = kwargs.get('max_retries', self.__DEFAULT_MAX_RETRIES)

    def __add_auth_header(self, req):
        """
        Adds the authorization header to the requests.PreparedRequest

        Args:
            req: requests.PreparedRequest for which to update the
            Authorization header.
        """
        # The signature uses an AWS/Azure-like scheme.
        signer = hmac.new(self.api_secret,
                          digestmod=hashlib.sha256)
        signer.update((req.method + '\n').encode('utf-8'))
        signer.update((req.path_url + '\n').encode('utf-8'))
        signer.update((req.headers.get('X-Tetration-Cksum', '') + '\n')
                      .encode('utf-8'))
        signer.update((req.headers.get('Content-Type', '') + '\n')
                      .encode('utf-8'))
        signer.update((req.headers.get('Timestamp', '') + '\n')
                      .encode('utf-8'))
        signature = base64.b64encode(signer.digest())
        req.headers['Authorization'] = signature

    def __add_custom_headers(self, req, checksum=True):
        """
        Adds custom headers to the request used by the backend for
        validation.

        Args:
            req: requests.PreparedRequest for which to update the
            Authorization header.
            kwargs:
                checksum: if True, a checksum is computed over the body

        Returns:
            Nothing
        """
        if req.body and checksum and req.method in ['POST', 'PUT', 'DELETE']:
            req.headers['X-Tetration-Cksum'] = (
                hashlib.sha256(req.body.encode('utf-8')).hexdigest()
            )
        req.headers['User-Agent'] = 'Cisco Tetration Python client'
        time_fmt = '%Y-%m-%dT%H:%M:%S+0000'
        # The time format above is hardcoded with +0000 for the time offset.
        # Use ISO 8601 standard?
        req.headers['Timestamp'] = datetime.utcnow().strftime(time_fmt)
        req.headers['Id'] = self.api_key

    def __load_credentials_from_file(self):
        """
        Private method to load api_key and api_secret from
        user specified json file.

        Args:
            NA

        Returns:
            Nothing
        """
        if '~' in self.credentials_file:
            homedir = os.path.expanduser('~')
            self.credentials_file = self.credentials_file.replace('~', homedir)

        with open(self.credentials_file) as credentials_file:
            credentials = json.load(credentials_file)

        try:
            self.api_key = credentials['api_key'].encode('ascii')
        except KeyError as _:
            raise KeyError('api_key missing in "%s" file' %
                           self.credentials_file)

        try:
            self.api_secret = credentials['api_secret'].encode('ascii')
        except KeyError as _:
            raise KeyError('api_secret missing in "%s" file' %
                           self.credentials_file)

    def __prefix_path(self, uri_path):
        if uri_path.startswith(self.uri_prefix):
            return uri_path
        else:
            return self.uri_prefix + uri_path

    def __send_request(self, req, retries, timeout):
        """
         Retries a request `retries` times. Returns a requests.Response.

         Args:
             req: requests.Request object for the request
             retries: Number of times to retry the request
             timeout: Float of timeout in seconds

         Returns:
             requests.Response object for the request
         """
        response = None
        for retry_count in range(retries):
            try:
                response = self.session.send(req,
                                             timeout=timeout,
                                             verify=self.verify)
            except requests.exceptions.RequestException:
                if retry_count == retries - 1:
                    raise
            else:
                if response.status_code not in self.__RETRY_HTTP_CODES:
                    return response
            time.sleep(self.__SLEEP_BETWEEN_RETRIES_SEC)
        return response

    def signed_http_request(self, http_method, uri_path, args=None):
        """
        Send a signed http request to the server. Returns a requests.Response.

        Args:
            http_method: String HTTP method like 'GET', 'PUT', 'POST', ...
            uri_path: Additional string URI path for query
            args: Additional dictionary of arguments
                "params": Additional dictionary of parameters for GET and PUT
                "json_body": String JSON body
                "timeout": Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        if http_method not in self.SUPPORTED_METHODS:
            warnings.warn('HTTP method "%s" is unsupported. Returning None' %
                          http_method)
            return None
        if not self.api_key or not self.api_secret:
            warnings.warn('API Key or Secret is missing. Returning None')
            return None

        args = {} if args is None else args
        params = args.get('params')
        json_body = args.get('json_body', '')
        timeout = args.get('timeout', self.__DEFAULT_TIMEOUT)
        unprep_req = requests.Request(
            http_method,
            urljoin(self.server_endpoint, uri_path),
            params=params,
            data=json_body)
        req = self.session.prepare_request(unprep_req)
        req.headers['Content-Type'] = 'application/json'
        self.__add_custom_headers(req)
        self.__add_auth_header(req)
        retries = 1
        if http_method in self.__RETRY_METHODS:
            retries = max(self.retries, 1)
        return self.__send_request(req, retries, timeout)

    def get(self, uri_path='', **kwargs):
        """
        Get request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                params: Additional dictionary of parameters for GET
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='GET', uri_path=self.__prefix_path(uri_path),
            args=kwargs)

    def post(self, uri_path='', **kwargs):
        """
        POST request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='POST', uri_path=self.__prefix_path(uri_path),
            args=kwargs)

    def put(self, uri_path='', **kwargs):
        """
        PUT request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='PUT', uri_path=self.__prefix_path(uri_path),
            args=kwargs)

    def delete(self, uri_path='', **kwargs):
        """
        DELETE request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='DELETE', uri_path=self.__prefix_path(uri_path),
            args=kwargs)
