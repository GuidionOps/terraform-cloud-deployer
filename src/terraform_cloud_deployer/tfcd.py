"""
Top level Terraform Cloud API CLI helper. See the commands imports inside for sub-commands
"""

import logging
import click
import os
import sys

from terraform_cloud_deployer import __version__

__author__ = "Afraz Ahmadzadeh"
__copyright__ = "Afraz Ahmadzadeh"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option("--tfc-organisation", '-o', default='guidion', help='Terraform Cloud organisation name')
@click.option("--tfc-api-token", '-t', help='Terraform Cloud API token')
@click.option("--tfc-workspace", '-w', help='Terraform Cloud workspace name', required=True)
def main(ctx, tfc_organisation, tfc_api_token, tfc_workspace):
    """
    Helper package for performing Terraform CI/CD operations. Also talks a bit to Slack ;)
    """

    try:
        tfc_api_token = tfc_api_token or os.environ['TERRAFORM_CLOUD_API_TOKEN']
        tfc_root_url = "https://app.terraform.io/api/v2"
    except KeyError:
        print("Please ensure that either the environment variable TERRAFORM_CLOUD_API_TOKEN is set, or you pass it in with the -t flag")
        sys.exit(1)

    ctx.obj = {
        'tfc_api_token': tfc_api_token,
        'tfc_organisation': tfc_organisation,
        'tfc_workspace': tfc_workspace,
        'tfc_root_url': tfc_root_url
    }

from terraform_cloud_deployer.terraform_cloud.commands import configuration as configuration_commands
from terraform_cloud_deployer.terraform_cloud.commands import run as run_commands
from terraform_cloud_deployer.communication.commands import communication as communication_commands
main.add_command(configuration_commands)
main.add_command(run_commands)
main.add_command(communication_commands)
