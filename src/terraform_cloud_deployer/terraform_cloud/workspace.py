"""
CLI methods for Terraform Cloud statefile operations

https://developer.hashicorp.com/terraform/cloud-docs/api-docs/state-versions
"""

import requests
import json
from pprint import pprint
import sys
import re
import time
import logging
import json

class Workspace():
    """ Methods for interactive with workspaces """

    def __init__(self, tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace):
        self.tfc_api_token = tfc_api_token
        self.tfc_root_url = tfc_root_url
        self.tfc_organisation = tfc_organisation
        self.tfc_workspace = tfc_workspace

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            workspace_response = requests.get(f"{self.tfc_root_url}/organizations/{tfc_organisation}/workspaces/{tfc_workspace}", headers=headers)
            workspace_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error getting information on workspace {self.tfc_workspace}. Does the token you're using have access to it?:\n{e}")
            sys.exit(1)

        self.workspace_id = workspace_response.json()['data']['id']

    def list_states(self, version):
        """ Give a list of state versions """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                f"{self.tfc_root_url}/state-versions?filter[workspace][name]={self.tfc_workspace}&filter[organization][name]={self.tfc_organisation}&filter[status]=finalized",
                headers=headers)

        except requests.exceptions.HTTPError as e:
            print(f"Error getting statefile:\n{e}")
            sys.exit(1)

        response_json = response.json()
        state_ids = [ {this_item['attributes']['created-at']: this_item['id']} for this_item in response_json['data'] ]

        return state_ids

    def get_state(self, version):
        """ Get a statefile """

        if version != None:
            state_url = f"{self.tfc_root_url}/state-versions/{version}"
        else:
            state_url = f"{self.tfc_root_url}/workspaces/{self.workspace_id}/current-state-version"

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                state_url,
                headers=headers)
        except requests.exceptions.HTTPError as e:
            print(f"Error getting statefile:\n{e}")
            sys.exit(1)

        response_json = response.json()
        state_download_url = response_json['data']['attributes']['hosted-state-download-url']
        state_file = requests.get(state_download_url, headers=headers)
        with open('downloaded-terraform.tfstate', 'w') as state_file_io:
            state_file_io.write(json.dumps(state_file.json(), indent=2))

        print("Wrote the statefile to 'downloaded-terraform.tfstate' in the current directory")
