"""
CLI methods for Terraform Cloud run handling

https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run
"""

import requests
import json
from pprint import pprint
import sys
import re
import time
import logging

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

    def start(self, configuration_id, wait):
        """ Start a run on [configuration_id] and return {run_url, run_id, plan_id} """

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

        run_id = response.json()['data']['id']
        plan_id = response.json()['data']['relationships']['plan']['data']['id']
        if wait:
            # TODO: If we print here, we'd have to write the outputs of the CICD commands to
            #       a file instead, else this output would be included to the next CICD job
            self.get_plan(plan_id)

        return json.dumps({
          "run_url": f"https://app.terraform.io/app/{self.tfc_organisation}/workspaces/{self.tfc_workspace}/runs/{run_id}",
          "run_id": run_id,
          "plan_id": plan_id
        })

    def get_plan_id(self, run_id):
        """ Get plan_id for [run_id] """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                f"{self.tfc_root_url}/runs/{run_id}",
                headers=headers)
        except requests.exceptions.HTTPError as e:
            print(f"Error getting plan:\n{e}")
            sys.exit(1)

        response_json = response.json()
        plan_id = response_json['data']['relationships']['plan']['data']['id']

        return plan_id

    def get_plan_information(self, plan_id):
        """
        Return information on [plan_id]
        """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                f"{self.tfc_root_url}/plans/{plan_id}",
                headers=headers)
        except requests.exceptions.HTTPError as e:
            print(f"Error getting plan:\n{e}")
            sys.exit(1)

        return response.json()

    def get_plan(self, plan_id):
        """
        Return a string representation of a parsed JSON plan of [plan_id].
        Can secretly also accept a run_id as [plan_id], and work out the plan_id
        """

        url_plan_matches = re.match('plan-.*', plan_id)
        if not url_plan_matches:
            plan_id = self.get_plan_id(plan_id)

        self.wait_for_plan(plan_id)

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.get(
                f"{self.tfc_root_url}/plans/{plan_id}/json-output",
                headers=headers)
        except requests.exceptions.HTTPError as e:
            print(f"Error getting plan:\n{e}")
            sys.exit(1)

        if response.status_code == 204:
            plan_information = self.get_plan_information(plan_id)
            status = plan_information['data']['attributes']['status']
            print(f"The status is listed as listed as '{status}', which means we can't fetch the plan")
            sys.exit(0)

        return parse_plan(response.json())

    def wait_for_plan(self, plan_id):
        """ Wait five minutes for a plan to finish, return False on timeout or error """

        status = self.get_plan_information(plan_id)['data']['attributes']['status']
        timeout = 300
        timer = 0
        while status != 'finished':
            if status in ['errored', 'cancelled', 'unreachable'] or timer >= timeout:
                print(f"The plan is irrecoverable, or the timeout has been reached. The last status report was: '{status}'")
                print(f"You can try again later by quering the plan '{plan_id}'")
                return False

            status = self.get_plan_information(plan_id)['data']['attributes']['status']
            logging.info(f"Plan status is currently '{status}'. Sleeping for 10 seconds and trying again")
            timer += 10
            time.sleep(10)

        return True

    def apply(self, run_id, comment=None):
        """ Attempt to apply a plan """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            response = requests.post(
                                    f"{self.tfc_root_url}/runs/{run_id}/actions/apply",
                                    headers=headers)
        except requests.exceptions.HTTPError as e:
            # print(f"Error starting a run in workspace {self.tfc_workspace} for configuration id {configuration_id}:\n{e}")
            sys.exit(1)

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

### Functions

def parse_plan(plan_json):
    """ Parse Terraform JSON plan into human readable string and return it"""

    parsed_output = {}

    for this_change in plan_json['resource_changes']:

        parsed_output[this_change['address']] = {
            'change_types': this_change['change']['actions'],
            'change_before': this_change['change']['before'],
            'change_after': this_change['change']['after']
        }

    return parsed_output
