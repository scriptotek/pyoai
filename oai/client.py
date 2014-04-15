import time
import logging
import requests
import urllib
from .response import Response
from .harvester import Harvester

logger = logging.getLogger()


class Client(object):

    def __init__(self, base_url,
                 metadata_format='http://www.loc.gov/MARC21/slim',
                 user_agent='PyOaiHarvester/0.1'):
        self.base_url = base_url.rstrip('?') + '?'
        self.format = ''
        self.headers = {'User-agent': user_agent}
        self.identify = self.identify().identify
        self.sets = self.list_sets().sets
        self.formats = self.list_metadata_formats().formats
        self.set_format(metadata_format)

    def help(self):
        """
        Output info about the sets and metadata formats supported by the data provider
        """
        print "Repo info:"
        print " - Name: %s" % (self.identify['repositoryName'])
        print " - URL: %s" % (self.base_url)
        print " - Protocol version: %s" % (self.identify['protocolVersion'])
        print " - Earliest datestamp: %s" % (self.identify['earliestDatestamp'])
        print " - Sets:"
        for oai_set in self.sets:
            print '    - %s : %s' % (oai_set['name'], oai_set['spec'])

        print " - Formats:"
        for oai_format in self.formats:
            print '    - %s : %s' % (oai_format['prefix'], oai_format['namespace'])

    def set_format(self, format_namespace):
        # TODO
        f = filter(lambda x: x['namespace'] == format_namespace, self.formats)
        if len(f) == 0:
            logger.warn('Metadata namespace "%s" not found in list of supported formats', format_namespace)
            return
        self.format = f[0]['prefix']

    def get(self, params):
        """
        Perform a single request and return a Response object
        """
        url = self.base_url + urllib.urlencode(params)
        print url
        response = requests.get(url, headers=self.headers)
        return Response(response.text)

    def identify(self):
        """
        Perform a single Identify request and return a Response object
        """
        return self.get({'verb': 'Identify'})

    def list_sets(self):
        """
        Perform a single ListSets request and return a Response object
        """
        return self.get({'verb': 'ListSets'})

    def list_metadata_formats(self):
        """
        Perform a single ListMetadataFormats request and return a Response object
        """
        return self.get({'verb': 'ListMetadataFormats'})

    def list_records(self, set_spec, date_from, date_until, resumption_token=''):
        """
        Perform a single ListRecords request and return an OaiResponse object
        """
        return self.get({
            'verb': 'ListRecords',
            'set': set_spec,
            'metadataPrefix': self.format,
            'from': date_from,
            'until': date_until,
            'resumptionToken': resumption_token
        })

    def harvest(self, set_spec, date_from, date_until):
        """
        Start harvesting
        """
        return Harvester(self, set_spec, date_from, date_until)
