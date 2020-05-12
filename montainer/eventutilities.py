import logging
from requests import get
import time
import docker

NOTIFIERS_TO_STRING = {'stop': {"Title": "A container stopped on server IP: {ip}, Date: {time}",
                                "Body": "Container name: {container}, image: ({image})",
                                },
                       'kill': {"Title": "A container stopped on server IP: {ip}, Date: {time}",
                                "Body": "Container name: {container}, image: ({image})",
                                },
                       'health_status: unhealthy': {"Title": "A container has failed a health test"
                                                             " on server IP: {ip}, Date: {time}",
                                                    "Body": "Container name: {container}, image: ({image}), logs: ({log})",
                                                    },
                       'Multiple': {"Title": "Multiple containers are having issues on IP: {ip}, Date: {time}",
                                    "Body": "Container name: {container} \nStatus: {status} \nImage: ({image})",
                                    "Body_unhealthy": "Container name: {container} \nStatus: {status} \nImage: ({image}) \nLogs=({log})"

                                    }
                       }

_IP = ''


def set_ip():
    global _IP
    _IP = get('https://api.ipify.org').text


class EventUtilities(list):
    """ This class extends the list class, and provides several functions for the main program. """
    def __getitem__(self, key):
        return super(EventUtilities, self).__getitem__(key-1)

    def return_index(self, event):
        """Returns the index of a event"""
        i = 0
        for events in self:
            if events.get("id") == event.get("id"):
                return i
            i += 1

    def exist_append(self, event):
        """Checks if a event exists through id search"""
        for events in self:
            if events.get("id") == event.get("id"):
                return True
        return False

    def exist_remove(self, event):
        """Checks if a event exists through id and docker-compose id"""
        global docker_compose_hash, docker_number
        try:
            docker_number = event.get("Actor")["Attributes"]["com.docker.compose.container-number"]
        except KeyError as ex:
            print("Could not find key: {0}. Montainer will compare without docker compose container number.".format(ex))

        try:
            docker_compose_hash = event.get("Actor")["Attributes"]['com.docker.compose.config-hash']
        except KeyError as ex:
            print("Could not find key: {0}. Montainer will compare without docker compose hash.".format(ex))

        for events in self:
            if events.get("id") == event.get("id"):
                logging.debug("Id Matches")
                self.remove(events)
                return True
            try:
                if event.get("Actor")["Attributes"]['com.docker.compose.config-hash'] == docker_compose_hash:
                    logging.debug("Found docker-compose config hash on the container:" + docker_compose_hash)
                    self.remove(events)
                    return True

                elif event.get("Actor")["Attributes"]['com.docker.compose.config-hash'] == docker_compose_hash and \
                        events.get('Actor')['Attributes']['com.docker.compose.container-number'] == docker_number:
                    logging.debug("Found docker-compose config hash and config id on the container:" + docker_number)
                    self.remove(events)
                    return True
            except KeyError as ex:
                logging.debug("Docker-compose is not used")
        return False

    def get_events_attributes(self, event):
        """Gathers the necessary event attributes, and return them"""
        client = docker.from_env()
        index = self.return_index(event)
        event = self.__getitem__(index)
        name = event.get("Actor")["Attributes"]["name"]
        image = event.get("Actor")["Attributes"]["image"]
        status = event.get("status")
        time_local = time.localtime(event.get("time"))
        time_format = "{}/{}/{} {}:{}:{}".format(
                                                 str(time_local[0]).zfill(2), str(time_local[1]).zfill(2),
                                                 str(time_local[2]).zfill(2), str(time_local[3]).zfill(2),
                                                 str(time_local[4]).zfill(2), str(time_local[5]).zfill(2),
        )
        c = client.containers.get(event.get('id'))
        try:
            container_log = c.attrs['State']['Health']['Log'][0]['Output'].rstrip()
            return name, image, status, time_format, container_log
        except KeyError as ex:
            print("Container does not have any health checks")

        return name, image, status, time_format

    def event_logger(self, event):
        """Returns a string of event attributes for logging"""
        name, image, status, time_format = self.get_events_attributes(event)
        return "Container: {}, image: {}, status: {}, time: {}".format(name, image, status, time_format)

    def build_text_event(self, event):
        """Return a string of event attributes for single notifications"""
        name, image, status, time_format, container_log = self.get_events_attributes(event)
        liste = NOTIFIERS_TO_STRING
        title = liste[status]['Title'].format(ip=_IP, container=name, time=time_format,)
        if status == "health_status: unhealthy":
            body = liste[status]['Body'].format(container=name, image=image, time=time_format, log=container_log)
        else:
            body = liste[status]['Body'].format(container=name, image=image, time=time_format)

        return title, body

    def build_test_event_list(self, events):
        """Return a string of event attributes as a summary of events"""
        name, image, status, time_format, container_log = self.get_events_attributes(events[0])
        liste = NOTIFIERS_TO_STRING
        title = liste['Multiple']['Title'].format(ip=_IP, time=time_format,)
        body = ""
        for event in events:
            name, image, status, time_format, container_log = self.get_events_attributes(event)
            if status == "health_status: unhealthy":
                body += liste['Multiple']['Body_unhealthy'].format(container=name, status=status, image=image, log=container_log) + "\n\n"
            else:
                body += liste['Multiple']['Body'].format(container=name, status=status, image=image) + "\n\n"
        return title, body
