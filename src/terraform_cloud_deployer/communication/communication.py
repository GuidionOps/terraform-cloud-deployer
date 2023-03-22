"""
An unfortunately non-generic class for sending communication about runs. It's specifically
designed for Slack communication at the moment
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class Communication():
    """ Non-generic communication class for sending messages about runs """

    def __init__ (self, run_url):
        self.run_url = run_url

    def compose_slack_run_block(self):
        """ Compose a message block for Slack """

        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "A deploy is waiting in acceptance or production"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Go to the Circle CI Job",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": self.run_url,
                    "action_id": "button-action"
                }
        }
        return block


    def send_slack_message(self, slack_channel, slack_token):
        """ Send a message to [slack_channel] """

        client = WebClient(token=slack_token)
        run_block = self.compose_slack_run_block()

        try:
            response = client.chat_postMessage(
                channel=slack_channel,
                blocks=[run_block]
            )
        except SlackApiError as e:
            print(f"Couldn't send a message to Slack:\n{e}")
