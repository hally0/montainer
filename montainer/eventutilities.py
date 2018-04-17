import time
from requests import get
# TODO write more utilities for event_list and optimize code

NOTIFIERS_TO_STRING = {'stop': {"Title": "A container stopped on server IP: {ip}, Date: {time}",
                                "Body": "Container name: {container}, image: ({image})",
                                },
                       'health_status: unhealthy': {"Title": "A container has failed a health test"
                                                             " on server IP: {ip}, Date: {time}",
                                                    "Body": "Container name: {container}, image: ({image})",
                                                    }
                       }


class EventUtilities(list):
    """ This class extends the list class, and will provide several functions for the main program. """
    def __getitem__(self, key):
        return super(EventUtilities, self).__getitem__(key-1)

    def return_index(self, event):
        """Returns the index of a event"""
        i = 0
        for events in self:
            if events.get("id") == event.get("id"):
                return i
            i += 1

    def exist(self, event):
        """Checks if a event exists"""
        for events in self:
            if events.get("id") == event.get("id"):
                return True
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

    def build_text(self, event):
        ip = get('https://api.ipify.org').text
        name, image, status, time_format = self.get_events_attributes(event)
        liste = NOTIFIERS_TO_STRING
        title = liste[status]['Title'].format(ip=ip, container=name, time=time_format,)
        body = liste[status]['Body'].format(container=name, image=image, time=time_format)
        return title, body
