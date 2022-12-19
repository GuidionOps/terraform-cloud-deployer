"""
CLI methods for Terraform Cloud run handling

https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run
"""

import requests
import json
from pprint import pprint
import sys

class Run():
    """ Methods for creating and interacting with Terraform Cloud runs """

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

    def start(self, configuration_id):
        """ Start a run on [configuration_id] and return {run_url, run_id} """

        run_data = json.dumps(
        {
          "data": {
            "attributes": {
              "message": "Test"
            },
            "type":"runs",
            "relationships": {
              "workspace": {
                "data": {
                  "type": "workspaces",
                  "id": f"{self.workspace_id}"
                }
              },
              "configuration-version": {
                "data": {
                  "type": "configuration-versions",
                  "id": f"{configuration_id}"
                }
              }
            }
          }
        })

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.post(
                                    f"{self.tfc_root_url}/runs",
                                    headers=headers,
                                    data=run_data)
        except requests.exceptions.HTTPError as e:
            print(f"Error starting a run in workspace {self.tfc_workspace} for configuration id {configuration_id}:\n{e}")
            sys.exit(1)

        run_id = response.json().get('data').get('id')

        return json.dumps({
          "run_url": f"https://app.terraform.io/app/{self.tfc_organisation}/workspaces/{self.tfc_workspace}/runs/{run_id}",
          "run_id": run_id
        })

    def cancel(self, run_id, comment=None):
        """
        Cancel _or_ discard the run [run_id]

        This will cancel a run if it's in progress, or discard a run if it's queued.

        Read up on 'cancel' and 'discard' here to see what that means:

        https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run#cancel-a-run
        https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run#discard-a-run
        """

        comment = comment or '{"comment": "Cancelled by the tfcd cancel command"}'
        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}

        try:
            requests.post(
                          f"{self.tfc_root_url}/runs/{run_id}/actions/cancel",
                          headers=headers,
                          data=comment)
            requests.post(
                          f"{self.tfc_root_url}/runs/{run_id}/actions/discard",
                          headers=headers,
                          data=comment)
        except Exception as e:
            print(f"Could not cancel run {run_id}: {e}")

    def list(self, full_output, filters):
        """ List runs for [self.workspace_id] """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}

        # TODO: Needs pagination. This only grabs the first page
        runs = requests.get(
                 f"{self.tfc_root_url}/workspaces/{self.workspace_id}/runs",
                 headers=headers,
                 params=filters)

        if runs.status_code != 200:
            errors = [message['detail'] for message in json.loads(runs.text)['errors']]
            for this_error in errors:
                print(this_error)
                sys.exit(1)

        if full_output:
            run_output = runs.json().get('data')
        else:
            run_output = []
            for this_run in runs.json().get('data'):
                run_id = this_run.get('id')
                created_at = this_run.get('attributes').get('created-at')
                status = this_run.get('attributes').get('status')
                status_timestamp = this_run.get('attributes').get('status_timestamp')
                run_url = f"{self.tfc_root_url}/runs/{run_id}"
                site_url = f"https://app.terraform.io/app/{self.tfc_organisation}/workspaces/{self.tfc_workspace}/runs/{run_id}"

                run_output.append({'id': run_id,
                                   'created_at': created_at,
                                   'status': status,
                                   'status_timestamp': status_timestamp,
                                   'run_url': run_url,
                                   'site_url': site_url})

        pprint(run_output)
