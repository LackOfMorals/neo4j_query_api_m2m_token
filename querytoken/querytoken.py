"""
 * Copyright (c) 2024-Present, Neo4j. and/or its affiliates. All rights reserved.
 *
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *
 * See the License for the specific language governing permissions and limitations under the License.
"""

# -*- coding: utf-8 -*-
# Generic/Built-in
import json
from typing import Dict

# Other Libs
from requests import Request, Session
from requests.auth import HTTPBasicAuth, AuthBase

# Owned




class MyConfiguration():
    CLIENT_ID = "YOUR_CLIENT_ID_FROM_OKTA"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET_FROM_OKTA"
    OKTA_TOKEN_URI = "YOUR_ACCOUNT_DOMAIN_FROM_OKTA/oauth2/default/v1/token"
    OKTA_SCOPE = "YOUR_SCOPE_FROM_OKTA"
    NEO4J_QUERY_URI = "YOUR_NEO4J_QUERY_URI"

class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def make_request(request_url: str, request_operation: str, request_headers: dict, request_body,
                 request_auth: AuthBase) -> Dict:
    """
   Makes a request to Aura API and returns the JSON from the response
   :param request_url The path to the endpoint to make a request to
   :param request_operation The HTTP operation to perform for the request
   :param request_headers  A dictionary containing headers for the request
   :param request_body  The body of the request
   :param request_auth  Auth to use with the request
   :return: The JSON response back as a Python Dict
   """

    # A session will be used to avoid having to make a new connection with each request
    request_session = Session()

    # Prepare our request
    prepared_request = Request(request_operation, request_url, headers=request_headers, auth=request_auth,
                               data=request_body).prepare()

    try:
        # Send the request
        response = request_session.send(prepared_request)

    except Exception as e:
        print("%s raised an error: \n%s", aura_api_request, e)
        raise

    else:
        return response.json()


def get_token_from_okta(url: str, client_id: str, client_secret: str, token_scope: str):
    """
   Gets a token from Okta
   :param url: URL for Okta token
   :param client_id: Okta client id
   :param client_secret: Okta client secret
   :param token_scope: Okta scope

   """
    # Ask for a bearer token using the client id and client secret from Okta

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    body = {"grant_type": "client_credentials", "scope": token_scope}

    okta_response = make_request(url, 'POST', headers, body, HTTPBasicAuth(client_id, client_secret))

    if 'access_token' in okta_response:
        return okta_response['access_token']
    else:
        return None


def get_data_from_neo4j(cypher_statement: str, query_api_url: str, token_from_okta: str) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    neo4j_response = make_request(query_api_url, 'POST', headers, cypher_statement, BearerAuth(token_from_okta))

    if 'data' in neo4j_response:
        return neo4j_response['data']
    else:
        return {}

    pass


def showcase_token_with_queryapi(config):

    okta_token = get_token_from_okta(config.OKTA_TOKEN_URI, config.CLIENT_ID, config.CLIENT_SECRET, config.OKTA_SCOPE)

    neo4j_query = {"statement": "MATCH (n) RETURN n LIMIT 1"}

    neo4j_data = get_data_from_neo4j(json.dumps(neo4j_query), config.NEO4J_QUERY_URI, okta_token)

    print(f"Data from Neo4j: {neo4j_data['values'][0]}")


if __name__ == '__main__':
    showcase_token_with_queryapi(MyConfiguration)
