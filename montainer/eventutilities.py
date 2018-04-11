import time

# TODO write more utilities for event_list and optimize code


class EventUtilities(list):
    """ This class extends the list class, and will provide several functions for the main program. """
    def __getitem__(self, key):
        return super(EventUtilities, self).__getitem__(key-1)

    def return_index(self, event):
        i = 0
        for events in self:
            if events.get('id') == event.get('id'):
                return i
            i += 1

    def exist(self, event):
        for events in self:
            if events.get('id') == event.get('id'):
                return True
        return False

    def get_events_attributes(self, event):
        index = self.return_index(event)
        event = self.__getitem__(index)
        name = event.get('Actor')['Attributes']['name']
        image = event.get('Actor')['Attributes']['image']
        status = event.get('status')
        time_local = time.localtime(event.get('time'))
        time_format = "{}/{}/{} {}:{}:{}".format(time_local[0], time_local[1], time_local[2]
                                                 , time_local[3], time_local[4], time_local[5])
        return name, image, status, time_format

    def event_general(self, event):
        name, image, status, time_format = self.get_events_attributes(event)
        return "Container: {}, image: {}, status: {}, time: {}".format(name, image, status, time_format)

    def event_title(self, event):
        name, image, status, time_format = self.get_events_attributes(event)
        if status == 'stop':
            return "Container: {}, is stopped, Date: {}".format(name, time_format)
        if status == 'health_status=unhealty':
            return "Container: {}, is unhealthy. Date: {}". format(name, time_format)
