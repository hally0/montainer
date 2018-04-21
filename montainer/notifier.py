from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import http.client
import logging
from montainer import config
from pushbullet import Pushbullet
import urllib.parse
import smtplib


""" This module acts as a central for notifying several different notifiers. It reads from the config file,
and makes a class for each available notifier. It also have several error detections for the configuration settings"""


_ENVIRONMENT_SETTINGS = {'PUSHBULLET': {'PB_TOKEN'},
                         'PUSHOVER': {'PO_TOKEN', 'USER_TOKEN'},
                         'EMAIL': {'SMTP_ADDRESS', 'SMTP_PORT', 'USERNAME', 'PASSWORD', 'FROM', 'TO'},
                         'SLACK': {},
                         'DISCORD': {}
                         }


def notifier_config():
    return config.Config("montainer.ini")


def get_class(notifier_name):
    """ Returns a class of the notifier. None if not found"""
    if notifier_name == "PUSHBULLET":
        return PushbulletNotifier(config_name=notifier_name,)
    if notifier_name == "PUSHOVER":
        return PushoverNotifier(config_name=notifier_name,)
    if notifier_name == "EMAIL":
        return EmailNotifier(config_name=notifier_name,)
    if notifier_name == "DISCORD":
        return DiscordNotifier(config_name=notifier_name,)
    if notifier_name == "SLACK":
        return SlackNotifier(config_name=notifier_name,)
    else:
        return None


def send_notifications(title, body):
    """ Sends out notification through all the available notifiers. If none of the notifiers return True, this function
    will return False"""
    _AVAILABLE_NOTIFIERS = notifier_config().get_notifiers()
    logging.debug("Available notifiers: {}".format(_AVAILABLE_NOTIFIERS))
    sent = False
    for notifiers in _AVAILABLE_NOTIFIERS:
        try:
            c = get_class(notifiers)
            if c is not None:
                if c.notify(title, body):
                    sent = True
        except KeyError:
            logging.debug("Montainer failed to send notification to {}").format(notifiers)
    if sent:
        return True
    return False


class Notifier(object):
    """ Notifier object that reads the appropriate section from the configuration file"""
    def __init__(self, config_name):
        self.config_section = None
        self.validate_settings(config_name)

    def validate_settings(self, config_name):
        # Validates settings before settings the config section
        config_settings = dict(notifier_config().get_section(config_name).items())
        settings_difference = [x for x in _ENVIRONMENT_SETTINGS[config_name] if x not in config_settings]
        if not len(settings_difference):
            self.config_section = notifier_config().get_section(config_name)
        else:
            logging.debug("""Configuration files does not fulfill the requirements of this class: {}.
                           missing keys are {}. Please update montainer.ini with the right information, and restart
                           the program""".format(config_name, settings_difference))
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
            logging.debug("""Failed to send Pushbullet notification. You might not have internet for the container. 
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
            return True
        except Exception as ex:
            logging.debug("""Failed to send Pushover notification. You might not have internet for the container. 
            Another cause might be a invalid Pushover API/user token. Please edit your tokens in montainer.ini.""")
            return False


class DiscordNotifier(Notifier):
    def notify(self, title, body):
        """ Sends a Discord notification"""
        try:

            return True
        except Exception as ex:
            logging.debug("""Failed to send Discord notification. You might not have internet for the container. 
            Another cause might be a invalid configuration settings. Please edit your settings in montainer.ini.""")
            return False


class SlackNotifier(Notifier):
    def notify(self, title, body):
        """ Sends a Slack notification"""
        try:

            return True
        except Exception as ex:
            logging.debug("""Failed to send Slack notification. You might not have internet for the container. 
            Another cause might be a invalid configuration settings. Please edit your settings in montainer.ini.""")
            return False


class EmailNotifier(Notifier):
    def notify(self, title, body):
        """ Sends a Email notification"""
        try:
            from_address = self.config_section['FROM']
            to_address = self.config_section['TO']
            msg = MIMEMultipart()
            msg['From'] = from_address
            msg['To'] = to_address
            msg['Subject'] = title
            body = body
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP(self.config_section['SMTP_ADDRESS'], self.config_section['SMTP_PORT'])
            if self.config_section['TLS']:
                server.starttls()
            server.login(from_address, self.config_section['PASSWORD'])

            text = msg.as_string()
            server.sendmail(self.config_section['FROM'], self.config_section['TO'], text)
            server.quit()
            return True

        except Exception as ex:
            logging.debug("""Failed to send Email notification. You might not have internet for the container. 
            Another cause might be a invalid configuration settings. Please edit your settings in montainer.ini.""")
            return False
