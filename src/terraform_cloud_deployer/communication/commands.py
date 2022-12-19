"""
Commands for sending communication to relevant places about Terraform Cloud runs
"""

import click
import os
import sys

@click.group
@click.pass_context
def communication(ctx): # pylint: disable=unused-argument
    """ Commands for sending communication to relevant places about Terraform Cloud runs """
    pass # pylint: disable=unnecessary-pass

@communication.command()
@click.option("--slack-channel", '-s', default='', help='Slack channel to send deploy URL to. Will try from environment if not provided')
@click.option('--slack-token', '-t', help='Slackbot token. Will try from environment if not provided')
@click.option('--run-url', '-u', help='URL of the TFC run to report', required=True)
@click.pass_context
def send(ctx, slack_channel, slack_token, run_url):
    """ Commands for sending communication to relevant places about TFC runs """

    try:
        slack_token = slack_token or os.environ["SLACK_ACCESS_TOKEN"]
    except KeyError:
        print("Ensure a token is provided either via the -t flag, or the SLACK_ACCESS_TOKEN environment variable")
        sys.exit(1)

    try:
        slack_channel = slack_channel or os.environ["SLACK_DEFAULT_CHANNEL"]
    except KeyError:
        print("Ensure a channel is provided either via the -s flag, or the SLACK_DEFAULT_CHANNEL environment variable")
        sys.exit(1)

    from terraform_cloud_deployer.communication import communication as communication_class
    communication_object = communication_class.Communication(run_url)

    communication_object.send_slack_message(slack_channel, slack_token)
