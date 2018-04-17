from pushbullet import Pushbullet
from montainer import config
import http.client
import urllib.parse
import logging

""" This module will be extended to act as a central for notifying several different devices through many options """

# TODO Extend class to support multiple notifiers and notifying stacks

_ENVIRONMENT_SETTINGS = {'PUSHBULLET': {'TOKEN'},
                         'PUSHOVER': {'TOKEN', 'USER'},
                         'EMAIL': {'test'},
                         }


def notifier_config():
    return config.Config("montainer.ini")


def get_class(notifier_name):
    if notifier_name == "PUSHBULLET":
        return PushbulletNotifier(config_name=notifier_name,)
    if notifier_name == "PUSHOVER":
        return PushoverNotifier(config_name=notifier_name,)
    if notifier_name == "EMAIL":
        return EmailNotifier(config_name=notifier_name,)
    else:
        return None


def send_notifications(title, body):
    _AVAILABLE_NOTIFIERS = notifier_config().get_notifiers()
    for notifiers in _AVAILABLE_NOTIFIERS:
        try:
            c = get_class(notifiers)
            if c is not None:
                c.notify(title, body)
        except KeyError:
            logging.debug("Montainer failed to send notification to {}").format(notifiers)
    return True


class Notifier(object):
    def __init__(self, config_name):
        self.config_section = None
        self.validate_settings(config_name)

    def validate_settings(self, config_name):
        config_settings = dict(notifier_config().get_section(config_name).items())
        settings_difference = set(config_settings).difference(_ENVIRONMENT_SETTINGS[config_name])
        if not len(settings_difference):
            self.config_section = notifier_config().get_section(config_name)
        else:
            logging.debug("""Configuration files does not fulfill the requirements of this class.
                           missing keys are {0}. Please update montainer.ini with the right information, and restart
                           the program""".format(settings_difference))
            return


class PushbulletNotifier(Notifier):
    def notify(self, title, body):
        """ Sends a Pushbullet notification"""
        try:
            api_key = self.config_section["PB_TOKEN"]
            pb = Pushbullet(api_key)
            push = pb.push_note(title, body)
            return True
        except Exception as ex:
            logging.debug(ex)
            logging.debug("""You might not have internet for the container. 
            Another cause might be a invalid Pushbullet API key. Please edit your API key in montainer.ini.""")
            return False


class PushoverNotifier(Notifier):
    def notify(self, title, body):
        """ Sends a Pushover notification"""

        try:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
                         urllib.parse.urlencode({
                          "token": self.config_section['PO_TOKEN'],
                          "user": self.config_section['USER_TOKEN'],
                          "title": title,
                          "message": body,
                         }), {"Content-type": "application/x-www-form-urlencoded"})
            conn.getresponse()
        except Exception as ex:
            print(ex)
            logging.debug("""You might not have internet for the container. 
            Another cause might be a invalid Pushover API/user token. Please edit your tokens in montainer.ini.""")
            return False
        return True


class EmailNotifier(Notifier):
    def notify(self, title, body):
        """ Sends a Pushbullet notification"""
        try:

            return True
        except Exception as ex:
            print(ex)
            logging.debug("""You might not have internet for the container. 
            Another cause might be a invalid Pushbullet API key. Please edit your API key in montainer.ini.""")
            return False
