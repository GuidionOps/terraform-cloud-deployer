"""
Top level Terraform Cloud API CLI helper. See the *_commands imports inside for sub-commands
"""

import logging
import click
import os

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
@click.option("--slack-channel", '-s', default='', help='Slack channel to send deploy URL to')
def main(ctx, tfc_organisation, tfc_api_token, tfc_workspace, slack_channel):
    """
    Top level Click group for commands. Passes all options down to sub-commands.
    """

    tfc_api_token = tfc_api_token or os.environ['TERRAFORM_CLOUD_API_TOKEN']
    tfc_root_url = f"https://app.terraform.io/api/v2"

    ctx.obj = {
        'tfc_api_token': tfc_api_token,
        'tfc_organisation': tfc_organisation,
        'tfc_workspace': tfc_workspace,
        'tfc_root_url': tfc_root_url,
        'slack_channel': slack_channel
    }

from terraform_cloud_deployer.terraform_cloud.commands import configuration as configuration_commands
from terraform_cloud_deployer.terraform_cloud.commands import run as run_commands
main.add_command(configuration_commands)
main.add_command(run_commands)
