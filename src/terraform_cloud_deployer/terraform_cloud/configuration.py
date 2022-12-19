"""
CLI methods for Terraform Cloud configuration run handling

https://developer.hashicorp.com/terraform/cloud-docs/api-docs/configuration-versions
"""

import tarfile
import glob
import datetime
import requests
import time
import sys

class Configuration():
    """ Methods for creating and interacting with Terraform Cloud configuration versions """

    def __init__(self, tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace):
        self.tfc_api_token = tfc_api_token
        self.tfc_root_url = tfc_root_url

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            workspace_info = requests.get(f"{self.tfc_root_url}/organizations/{tfc_organisation}/workspaces/{tfc_workspace}", headers=headers).raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get information for workspace {tfc_workspace}:\n{e}")
            sys.exit(1)

        self.workspace_id = workspace_info.json().get('data').get('id')

    def create(self, terraform_directory, code_directory):
        """ Create and upload a configuration version from [terraform_directory], [code_directory] """

        data_file = package_configuration(terraform_directory, code_directory)
        configuration_version = self.create_configuration()
        self.upload_configuration(configuration_version, data_file.name)

        return configuration_version.get('configuration_id')

    def create_configuration(self):
        """ Create new configuration version, return {configuration_id, upload_url} for use """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        response = requests.post(
                                  f"{self.tfc_root_url}/workspaces/{self.workspace_id}/configuration-versions",
                                  headers=headers,
                                  data='{"data":{"type":"configuration-versions", "attributes":{"auto-queue-runs": false}}}')

        configuration_id = response.json().get('data').get('id')
        upload_url = response.json().get('data').get('attributes').get('upload-url')

        return {'configuration_id': configuration_id, 'upload_url': upload_url}

    def upload_configuration(self, configuration_version, data_file):
        """ Upload data (Terraform code) to [configuration_version] """

        this_file = {'file': open(data_file, 'rb')}

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        response = requests.put(
                                  configuration_version.get('upload_url'),
                                  headers=headers,
                                  files=this_file)

        while self.get_configuration_info(configuration_version.get('configuration_id')).json().get('data').get('attributes').get('status') != 'uploaded':
            print("Configuration version is not ready yet")
            time.sleep(2)

    def get_configuration_info(self, configuration_id):
        """ Enter a wait loop for configuration status to change to 'uploaded' """

        headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        configuration_info = requests.get(
                                  f"{self.tfc_root_url}/configuration-versions/{configuration_id}",
                                  headers=headers)

        return configuration_info



    # CONFIGURATION_VERSION_STATUS=$(curl -f -s\
    #     --header "Authorization: Bearer $TERRAFORM_CLOUD_API_TOKEN" \
    #     --header "Content-Type: application/vnd.api+json" \
    #     --request GET \
    #     https://app.terraform.io/api/v2/configuration-versions/$CONFIGURATION_ID \
    #     | jq -r '.data.attributes.status')
    # }

# # Wait for the configuration version to be ready
# get_configuration_status
# while [[ "$CONFIGURATION_VERSION_STATUS" != "uploaded" ]]; do
#   get_configuration_status

#   echo "Configuration version is: $CONFIGURATION_VERSION_STATUS"
#   sleep 2
# done



# Functions

def package_configuration(terraform_directory, code_directory):
    """ Tar and Gzip the TFC configuration from [terraform_directory] and [code_directory] """

    this_date = datetime.datetime.now().isoformat()
    terraform_files = glob.glob(f"{terraform_directory}/*.tf")

    with tarfile.open(f"{this_date}.tar.gz", "w:gz") as tar_file:
        tar_file.add(code_directory)

        for name in terraform_files:
            tar_file.add(name)

    return tar_file
