"""
Commands for handling configuration versions and runs in Terraform Cloud
"""

import click
import re
from pprint import pprint
import sys

@click.group
@click.pass_context
def configuration(ctx): # pylint: disable=unused-argument
    """ Commands for handling configuration versions and runs for Terraform Cloud """
    pass # pylint: disable=unnecessary-pass

@configuration.command(name='list')
@click.pass_context
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
def list_configurations(ctx, tfc_workspace):
    """ List configuration versions for this workspace """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import configuration as configuration_class
    configuration_object = configuration_class.Configuration(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    configuration_object.list()

@configuration.command()
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.argument("configuration-id")
@click.pass_context
def show(ctx, tfc_workspace, configuration_id):
    """ Show some formatted and pre-selected information about a configuration version """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import configuration as configuration_class
    configuration_object = configuration_class.Configuration(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    configuration_object.show(configuration_id)

@configuration.command()
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.argument("configuration-id")
@click.pass_context
def download(ctx, tfc_workspace, configuration_id):
    """ Download the configuration package for [configuration-id] """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import configuration as configuration_class
    configuration_object = configuration_class.Configuration(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    configuration_object.download(configuration_id)

@configuration.command()
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.option('--terraform-directory', '-t', help='Where the Terraform files can be found', default='.')
@click.option('--code-directory', '-c', help='Where the application code can be found', required=True)
@click.pass_context
def create(ctx, tfc_workspace, terraform_directory, code_directory):
    """ Create and upload a Terraform Cloud configuration object """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

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
@click.option('--tfc-workspace', help='Workspace name to operate on', required=False)
@click.option('--configuration-id', '-c', help='Configuration ID to queue the run for', required=True)
@click.option('--wait', '-w', is_flag=True, help='Whether to wait for the output of the plan (and output it)', default=False)
@click.pass_context
def queue(ctx, tfc_workspace, configuration_id, wait):
    """ Add <configuration_id> (configuration version) to the run queue """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_id = run_object.queue(configuration_id, wait)
    print(run_id)

@run.command()
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.argument('plan_id')
@click.pass_context
def show_plan(ctx, tfc_workspace, plan_id):
    """ Get and print <plan_id> WARNING: Only works with admin generated runs """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    output = run_object.get_plan(plan_id)
    from pprint import pprint
    pprint(output)

@run.command()
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.option('--comment', '-m', help='Optional comment on why this is happening', default=None)
@click.pass_context
def apply(ctx, tfc_workspace, run_id, comment):
    """ Try to apply a plan """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    # output = run_object.apply(run_id, comment)
    # print(output)

@run.command()
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.argument('run-id', required=True)
@click.option('--auto-approve', '-a', is_flag=True, default=False, help='If used, will not ask for approval')
@click.option('--comment', '-c', help='Optional comment to add to the cancellaton call')
@click.option('--force', '-f', is_flag=True, default=False, help="Force cancel a run, whether it's currently running or not")
@click.pass_context
def cancel(ctx, tfc_workspace, run_id, auto_approve, force, comment):
    """ Cancel <run_id> or 'current' for latest run — use with caution on scheduled runs """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_object.cancel(run_id, auto_approve=auto_approve, force=force, comment=comment)

@run.command(name='list')
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.option('--full-output', '-o', help='Whether or not to print the full JSON output', is_flag=True, default=False)
@click.option('--filters', '-f', help='[status|user|page|operation|source|search]=values. Invalid filters are ignored', multiple=True)
@click.pass_context
def list_runs(ctx, tfc_workspace, full_output, filters):
    """ List runs in <workspace_id> """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_workspace = ctx.obj['tfc_workspace']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import run as run_class
    run_object = run_class.Run(tfc_api_token, tfc_root_url, tfc_organisation, tfc_workspace)

    run_object.list(full_output, format_filters(filters))

@click.group
@click.pass_context
def workspace(ctx): # pylint: disable=unused-argument
    """ Commands for working with workspaces """
    pass

@workspace.command()
@click.pass_context
def list_workspaces(ctx):
    """ List the most recent statefiles available """

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_root_url = ctx.obj['tfc_root_url']

    from terraform_cloud_deployer.terraform_cloud import workspace as workspace_class
    workspace_object = workspace_class.Workspace(tfc_api_token, tfc_root_url, tfc_organisation)

    workspaces = workspace_object.list_workspaces()
    pprint(workspaces)

@workspace.command()
@click.pass_context
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.option('--version', '-v', help='WIP: Run version to fetch state for')
def list_states(ctx, tfc_workspace, version):
    """ List the most recent statefiles available """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_root_url = ctx.obj['tfc_root_url']
    tfc_workspace = ctx.obj['tfc_workspace']

    from terraform_cloud_deployer.terraform_cloud import workspace as workspace_class
    workspace_object = workspace_class.Workspace(tfc_api_token, tfc_root_url, tfc_organisation)

    state_files = workspace_object.list_states(tfc_workspace, version)
    pprint(state_files)

@workspace.command()
@click.pass_context
@click.option('--tfc-workspace', '-w', help='Workspace name to operate on', required=False)
@click.option('--version', '-v', help='Run version to fetch state for')
def get_state(ctx, tfc_workspace, version):
    """ Fetch the latest (by default) statefile for <tfc_workspace> """

    ctx = workspace_deprecation_hack(ctx, tfc_workspace)

    tfc_api_token = ctx.obj['tfc_api_token']
    tfc_organisation = ctx.obj['tfc_organisation']
    tfc_root_url = ctx.obj['tfc_root_url']
    tfc_workspace = ctx.obj['tfc_workspace']

    from terraform_cloud_deployer.terraform_cloud import workspace as workspace_class
    workspace_object = workspace_class.Workspace(tfc_api_token, tfc_root_url, tfc_organisation)

    state_file = workspace_object.get_state(tfc_workspace, version)

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

def workspace_deprecation_hack(ctx, tfc_workspace):
    """
    Nast temporary hack to ensure the top level -w still works until it's
    removed
    """

    if ctx.obj['tfc_workspace'] == None:
        if tfc_workspace == None:
            print("Workspace must either be given as an argument to this command, or as an option (-w) at the top level")
            sys.exit(1)

        ctx.obj.update({'tfc_workspace': tfc_workspace})

    return ctx
