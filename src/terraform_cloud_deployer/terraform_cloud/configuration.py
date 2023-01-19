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
import logging

class Configuration():
    """ Methods for creating and interacting with Terraform Cloud configuration versions """

    def __init__(self, tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace):
        self.tfc_api_token = tfc_api_token
        self.tfc_root_url = tfc_root_url

        self.headers = {'Authorization': f"Bearer {self.tfc_api_token}", 'Content-Type': 'application/vnd.api+json'}
        try:
            workspace_info = requests.get(f"{self.tfc_root_url}/organizations/{tfc_organisation}/workspaces/{tfc_workspace}", headers=self.headers)
            workspace_info.raise_for_status()
            self.workspace_id = workspace_info.json().get('data').get('id')
        except (requests.exceptions.HTTPError, AttributeError) as e:
            print(f"Failed to get information for workspace '{tfc_workspace}'")
            logging.error(e)
            print("Check supplied token and workspace")
            sys.exit(1)

    def show(self, configuration_id):
        """ Print and return information about [configuration_id] """

        cv_full = requests.get(f"{self.tfc_root_url}/configuration-versions/{configuration_id}",
                               headers=self.headers)

        from pprint import pprint
        pprint(cv_full.json())
        return cv_full

    def list(self):
        """ List and return configuration IDs for this workspace """

        response = requests.get(f"{self.tfc_root_url}/workspaces/{self.workspace_id}/configuration-versions",
                               headers=self.headers).json()
        cvs = response['data']

        cv_list = []
        for this_cv in cvs:
            cv_list.append(this_cv['id'])

        print(cv_list)
        return cv_list

    def download(self, configuration_id):
        """ Download the configuration file of [configuration_id] """

        local_filename = f"{configuration_id}.tar.gz"
        cv_download_url = f"{self.tfc_root_url}/configuration-versions/{configuration_id}/download"
        with requests.get(cv_download_url, stream=True, headers=self.headers) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
        return local_filename

    def create(self, terraform_directory, code_directory):
        """ Create and upload a configuration version from [terraform_directory], [code_directory] """

        data_file = package_configuration(terraform_directory, code_directory)
        configuration_version = self.create_configuration()
        self.upload_configuration(configuration_version, data_file.name)

        return configuration_version.get('configuration_id')

    def create_configuration(self):
        """ Create new configuration version, return {configuration_id, upload_url} for use """

        response = requests.post(f"{self.tfc_root_url}/workspaces/{self.workspace_id}/configuration-versions",
                                 headers=self.headers,
                                 data='{"data":{"type":"configuration-versions", "attributes":{"auto-queue-runs": false}}}')

        configuration_id = response.json().get('data').get('id')
        upload_url = response.json().get('data').get('attributes').get('upload-url')

        return {'configuration_id': configuration_id, 'upload_url': upload_url}

    def upload_configuration(self, configuration_version, data_file):
        """ Upload data (Terraform code) to [configuration_version] """

        this_file = open(data_file, 'rb')

        these_headers = self.headers
        these_headers['Content-Type'] = "application/octet-stream"
        requests.put(configuration_version.get('upload_url'), headers=these_headers, data=this_file)

        while self.get_configuration_info(configuration_version.get('configuration_id')).json().get('data').get('attributes').get('status') != 'uploaded':
            logging.info("Configuration version is not ready yet")
            time.sleep(2)

    def get_configuration_info(self, configuration_id):
        """ Fetch and return information on [configuration_id] """

        configuration_info = requests.get(
                                  f"{self.tfc_root_url}/configuration-versions/{configuration_id}",
                                  headers=self.headers)

        return configuration_info

# Functions

def package_configuration(terraform_directory, code_directory):
    """ Tar and Gzip the TFC configuration from [terraform_directory] and [code_directory] """

    this_date = datetime.datetime.now().isoformat()
    terraform_files = glob.glob(f"{terraform_directory}/*.tf")

    try:
        with tarfile.open(f"{this_date}.tar.gz", "w:gz") as tar_file:
            tar_file.add(code_directory)

            for name in terraform_files:
                tar_file.add(name)
    except FileNotFoundError:
        logging.error(f"File/directory {code_directory} does not exist")
        sys.exit(1)

    return tar_file
