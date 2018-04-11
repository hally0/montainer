import configparser
import logging

# TODO Write tests and update class with more sections


class Config(object):
    """ This class reads from a configuration file and will provide several utilities for configuration files """

    def __init__(self, config_file):
        self._config_file = config_file
        self._config = configparser.ConfigParser()
        self._config.read(self._config_file)

    def exist(self, config):
        pass

    def write(self):
        pass

    def get_sections(self, section):
        try:
            section = self._config[section]
        except KeyError as ex:
            logging.debug("Couldn't find the section")
            return
        return section

    def get_key(self, section, key):
        try:
            key = self._config[section][key]
        except KeyError as ex:
            logging.debug("Couldn't find the key")
            return
        return key