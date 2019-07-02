from slacker import Slacker

import requests
import settings
import urllib


class SlackAlert(object):
    def __init__(self, token):
        self.token = token

    def send_message(self, baseurl, param):
        url = f"{baseurl}?token={self.token}&{urllib.parse.urlencode(param)}"
        requests.get(url)


def main():
    sa = SlackAlert(settings.RUMIN_TOKEN)

    params = {
        "channel": settings.ON_ON_BOT_TEST,
        "text": "Webhook test"
    }

    sa.send_message("https://slack.com/api/chat.postMessage", params)


if __name__ == "__main__":
    main()
