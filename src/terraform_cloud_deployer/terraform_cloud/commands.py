"""
Commands for handling configuration versions
"""

import click
import re
import ast

@click.group
@click.pass_context
def configuration(ctx): # pylint: disable=unused-argument
    """ Commands for handling configuration versions """
    pass # pylint: disable=unnecessary-pass

@configuration.command()
@click.option('--terraform-directory', '-t', help='Where the Terraform files can be found', default='.')
@click.option('--code-directory', '-c', help='Where the application code can be found', default='lambdas')
@click.pass_context
def create(ctx, terraform_directory, code_directory):
    """ Create and upload a Terraform Cloud configuration object """

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']
    slack_channel = ctx.obj['slack_channel']

    from terraform_cloud_deployer.terraform_cloud import configuration as configuration_class
    configuration_object = configuration_class.Configuration(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    configuration_id = configuration_object.create(terraform_directory, code_directory)
    print(configuration_id)

@click.group
@click.pass_context
def run(ctx): # pylint: disable=unused-argument
    """ Commands for handling runs """
    pass # pylint: disable=unnecessary-pass

@run.command()
@click.option('--configuration-id', '-c', help='Configuration ID to start the run for', required=True)
@click.pass_context
def start(ctx, configuration_id):
    """ Create and upload a Terraform Cloud configuration object """

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']
    slack_channel = ctx.obj['slack_channel']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_id = run_object.start(configuration_id)
    print(run_id)

@run.command()
@click.option('--run-id', '-r', help='Run ID to delete', required=True)
@click.pass_context
def cancel(ctx, run_id):
    """ Cancel [run_id]. Use with caution on scheduled runs """

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']
    slack_channel = ctx.obj['slack_channel']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_object.cancel(run_id)

@run.command(name='list')
@click.option('--full-output', '-f', help='Whether or not to print the full JSON output', is_flag=True, default=False)
# TODO:
# @click.option('--filters', '-i', help='[status|user]=values. Invalid filters are ignored', multiple=True)
@click.pass_context
def list_runs(ctx, full_output):
    """ List runs in [workspace_id] """

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']
    slack_channel = ctx.obj['slack_channel']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_object.list(full_output)
