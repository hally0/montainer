import configparser
import logging

# TODO Write tests and update class with more sections

NOTIFIERS_LIST = dict(PUSHBULLET="PushbulletNotifier", PUSHOVER="PushoverNotifier", EMAIL="EmailNotifier")

# Making a validate method
_CONFIG_SETTINGS = {"_SYNCTIME": (int, "GENERAL", 1),
                    "_DOWNTIME": (int, "GENERAL", 30),
                    "PB_TOKEN": (str, "PUSHBULLET", ""),
                    "PO_TOKEN": (str, "PUSHOVER", ""),
                    "USER_TOKEN": (str, "PUSHOVER", ""),
                    }


class Config(object):
    """ This class reads from a configuration file and will provide several utilities for configuration files """

    def __init__(self, config_file):
        self._config_file = config_file
        self._config = configparser.ConfigParser()
        self._config.optionxform = str
        try:
            self._config.read_file(open(self._config_file))
        except FileNotFoundError:
            print("Couldn't find the configuration file. Please make sure it exists within the docker container")
            exit(-1)
        self._config.read(self._config_file)

    def get_section(self, section):
        """Return a section of the config"""
        try:
            section = self._config[section]
        except configparser.NoSectionError and KeyError as ex:
            logging.debug("Couldn't find the section")
            return False
        return section

    def get_sections(self):
        """Return a section of the config"""
        try:
            sections = self._config.sections()
        except configparser.NoSectionError as ex:
            logging.debug("Couldn't find the section")
            return
        return sections

    def get_notifiers(self):
        config = self._config.sections()
        return set(config).intersection(NOTIFIERS_LIST)

    def get_key(self, section, key):
        """return a key of the config"""
        try:
            key = self._config[section][key]
        except configparser.NoSectionError as ex:
            logging.debug("Couldn't find the key")
            return
        return key