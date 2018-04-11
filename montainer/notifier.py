from pushbullet import Pushbullet
from montainer import config
""" This module will be extended to act as a central for notifying several different devices through many options """

# TODO Extend class to support multiple notifiers and notifying stacks
#class Notifier:

#    def __init__(self, conf):
#        self.config = config.Config.get_sections()


class Notifier:
    def __init__(self):
        config_file = config.Config('montainer.ini')
        self.config_section = config_file.get_sections('PUSHBULLET')

    def send_pushbullet(self, title, body):
        api_key = self.config_section['TOKEN']
        pb = Pushbullet(api_key)
        push = pb.push_note(title, body)


