import logging
from requests import get
import time

NOTIFIERS_TO_STRING = {'stop': {"Title": "A container stopped on server IP: {ip}, Date: {time}",
                                "Body": "Container name: {container}, image: ({image})",
                                },
                       'health_status: unhealthy': {"Title": "A container has failed a health test"
                                                             " on server IP: {ip}, Date: {time}",
                                                    "Body": "Container name: {container}, image: ({image})",
                                                    },
                       'Multiple': {"Title": "Multiple containers are having issues on IP: {ip}, Date: {time}",
                                    "Body": "Container name: {container} \nStatus: {status} \nImage: ({image})"

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
        docker_number = event.get("Actor")["Attributes"]["com.docker.compose.container-number"]
        for events in self:
            if events.get("id") == event.get("id"):
                logging.debug("Id Matches")
                self.remove(events)
                return True
            try:
                if events.get('Actor')['Attributes']['com.docker.compose.container-number'] == docker_number:
                    logging.debug("Found docker-compose number label on the container:" + docker_number)
                    self.remove(events)
                    return True
            except KeyError:
                logging.debug("Could not find the label or id.")
                return False

        return False

    def get_events_attributes(self, event):
        """Gathers the necessary event attributes, and return them"""
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
        return name, image, status, time_format

    def event_logger(self, event):
        """Returns a string of event attributes for logging"""
        name, image, status, time_format = self.get_events_attributes(event)
        return "Container: {}, image: {}, status: {}, time: {}".format(name, image, status, time_format)

    def build_text_event(self, event):
        """Return a string of event attributes for single notifications"""
        name, image, status, time_format = self.get_events_attributes(event)
        liste = NOTIFIERS_TO_STRING
        title = liste[status]['Title'].format(ip=_IP, container=name, time=time_format,)
        body = liste[status]['Body'].format(container=name, image=image, time=time_format)
        return title, body

    def build_test_event_list(self, events):
        """Return a string of event attributes as a summary of events"""
        name, image, status, time_format = self.get_events_attributes(events[0])
        liste = NOTIFIERS_TO_STRING
        title = liste['Multiple']['Title'].format(ip=_IP, container=name, time=time_format,)
        body = ""
        for event in events:
            name, image, status, time_format = self.get_events_attributes(event)
            body += liste['Multiple']['Body'].format(container=name, status=status, image=image) + "\n\n"
        return title, body
