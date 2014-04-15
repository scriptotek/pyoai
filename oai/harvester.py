import time
import logging
from .response import Response

logger = logging.getLogger()


class Harvester(object):

    def __init__(self, client, set_spec, date_from, date_until):
        self.client = client
        self.set_spec = set_spec
        self.date_from = date_from
        self.date_until = date_until

        f = filter(lambda x: x['spec'] == set_spec, client.sets)
        if len(f) == 0:
            logger.warn('Set "%s" not found in list of available sets', set_spec)
            return

        self.resumption_token = ''

    def __iter__(self):
        return self

    def next(self):

        if self.resumption_token is None:
            print "COMPLETE"
            raise StopIteration

        while True:
            #try:
            print "GET"
            response = self.client.list_records(self.set_spec, self.date_from,
                                                self.date_until, self.resumption_token)
            break
            # except:
            #     print "FAILED. Sleeping 5 secs"
            #     time.sleep(5)
        self.resumption_token = response.resumption_token
        print self.resumption_token
        return response
