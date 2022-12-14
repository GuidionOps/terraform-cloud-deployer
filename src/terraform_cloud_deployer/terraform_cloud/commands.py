"""
Commands for handling configuration versions and runs in Terraform Cloud
"""

import click
import re

@click.group
@click.pass_context
def configuration(ctx): # pylint: disable=unused-argument
    """ Commands for handling configuration versions and runs for Terraform Cloud """
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

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_object.cancel(run_id)

@run.command(name='list')
@click.option('--full-output', '-o', help='Whether or not to print the full JSON output', is_flag=True, default=False)
@click.option('--filters', '-f', help='[status|user|page|operation|source|search]=values. Invalid filters are ignored', multiple=True)
@click.pass_context
def list_runs(ctx, full_output, filters):
    """ List runs in [workspace_id] """

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_object.list(full_output, format_filters(filters))

# Helper functions

def format_filters(arguments):
    """
    Takes a tuple of [arguments], returns a dict formatted to be usable as
    either 'filter' or 'search' arguments. Abstracts away the need to know
    which is which.

    See here for differences:

    https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run#query-parameters
    """

    formatted_arguments = {}

    for argument in arguments:
        split_argument = argument.split('=')
        if split_argument[0] in ['user', 'status', 'page', 'operation', 'source', 'search']:

            formatted_argument = {
                "user": re.sub('(user)', 'search[\\1]', split_argument[0]),
                "status": re.sub('(status)', 'filter[\\1]', split_argument[0]),
                "page": re.sub('(page)', 'page[number]', split_argument[0]),
                "operation": re.sub('(operation)', 'filter[operation]', split_argument[0]),
                "source": re.sub('(source)', 'filter[source]', split_argument[0]),
                "search": re.sub('(search)', 'search[basic]', split_argument[0]),
            }

            formatted_arguments[formatted_argument[split_argument[0]]] = split_argument[1]

    return formatted_arguments
