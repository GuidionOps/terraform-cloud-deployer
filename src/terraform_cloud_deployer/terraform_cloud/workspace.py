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

    def __init__(self, tfc_api_token, tfc_root_url, tfc_organisation):
        self.tfc_api_token = tfc_api_token
        self.tfc_root_url = tfc_root_url
        self.tfc_organisation = tfc_organisation

    def list_workspaces(self):
        """ Give a list of all workspaces """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}

        next_page=1
        workspace_names = []
        while next_page:
            try:
                response = requests.get(
                    f"{self.tfc_root_url}/organizations/{self.tfc_organisation}/workspaces?page[size]=100&page[number]={next_page}",
                    headers=headers)
            except requests.exceptions.HTTPError as e:
                print(f"Error getting a list of workspaces:\n{e}")
                sys.exit(1)

            response_json = response.json()
            [ workspace_names.append(this_name['attributes']['name']) for this_name in response_json['data']]
            next_page = response_json['meta']['pagination']['next-page']

        return workspace_names

    def list_states(self, tfc_workspace, version):
        """ Give a list of state versions """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                f"{self.tfc_root_url}/state-versions?filter[workspace][name]={tfc_workspace}&filter[organization][name]={self.tfc_organisation}&filter[status]=finalized",
                headers=headers)

        except requests.exceptions.HTTPError as e:
            print(f"Error getting statefile:\n{e}")
            sys.exit(1)

        response_json = response.json()
        try:
            state_ids = [ {this_item['attributes']['created-at']: this_item['id']} for this_item in response_json['data'] ]
        except KeyError:
            print(f"There was a problem getting a listing of statefiles for the workspace '{tfc_workspace}'. Are there any states to fetch?")
            sys.exit(1)


        return state_ids

    def get_workspace_id(self, tfc_workspace):
        """ Return the workspace ID for [workspace] """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            workspace_response = requests.get(f"{self.tfc_root_url}/organizations/{self.tfc_organisation}/workspaces/{tfc_workspace}", headers=headers)
            workspace_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error getting information on workspace {tfc_workspace}. Does the token you're using have access to it?:\n{e}")
            sys.exit(1)

        return workspace_response.json()['data']['id']

    def get_state(self, tfc_workspace, version):
        """ Get a statefile """

        if version != None:
            state_url = f"{self.tfc_root_url}/state-versions/{version}"
        else:
            state_url = f"{self.tfc_root_url}/workspaces/{self.get_workspace_id(tfc_workspace)}/current-state-version"

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                state_url,
                headers=headers)
        except requests.exceptions.HTTPError as e:
            print(f"Error getting statefile:\n{e}")
            sys.exit(1)

        response_json = response.json()
        try:
            state_download_url = response_json['data']['attributes']['hosted-state-download-url']
        except KeyError:
            print(f"There was a problem getting the statefile for the workspace '{tfc_workspace}'. Are there any states to fetch?")
            sys.exit(1)
        state_file = requests.get(state_download_url, headers=headers)
        with open('downloaded-terraform.tfstate', 'w') as state_file_io:
            state_file_io.write(json.dumps(state_file.json(), indent=2))

        print("Wrote the statefile to 'downloaded-terraform.tfstate' in the current directory")
