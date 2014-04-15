import re
import logging
from lxml import etree

logger = logging.getLogger()


class Response(object):

    def __init__(self, text):
        self.raw_response = text
        #print text
        reader = XmlReader({'oai': 'http://www.openarchives.org/OAI/2.0/'})
        root = reader.parse(text.encode('utf-8'))

        if root.xpath('oai:error'):
            raise Exception(root.xpath('oai:error')[0].text())

        self.verb = root.xpath('oai:request')[0].attr('verb')
        #funcmap = {'ListSets' : self.ListSets}
        responses = {
            'Identify': self.read_identify,
            'ListSets': self.read_sets,
            'ListMetadataFormats': self.read_metadata_formats,
            'ListRecords': self.read_records
        }
        responses[self.verb](root)

    def read_identify(self, root):
        node = root.xpath('oai:Identify')[0]
        self.identify = {
            'repositoryName': node.text('oai:repositoryName'),
            'baseUrl': node.text('oai:baseUrl'),
            'protocolVersion': node.text('oai:protocolVersion'),
            'adminEmail': node.text('oai:adminEmail'),
            'earliestDatestamp': node.text('oai:earliestDatestamp'),
            'deletedRecord': node.text('oai:deletedRecord'),
            'granularity': node.text('oai:granularity')
        }

    def read_sets(self, root):
        sets = []
        for set_node in root.xpath('oai:ListSets/oai:set'):
            sets.append({
                'name': set_node.text('oai:setName'),
                'spec': set_node.text('oai:setSpec'),
            })
        self.sets = sets

    def read_metadata_formats(self, root):
        formats = []
        for format_node in root.xpath('oai:ListMetadataFormats/oai:metadataFormat'):
            formats.append({
                'prefix': format_node.text('oai:metadataPrefix'),
                'schema': format_node.text('oai:schema'),
                'namespace': format_node.text('oai:metadataNamespace')
            })
        self.formats = formats

    def read_records(self, root):
        print " --- read records ---"
        records = []
        for record in root.xpath('oai:ListRecords/oai:record'):
            records.append({
                'timestamp': record.text('oai:header/oai:datestamp'),
                'metadata': record.xpath('oai:metadata')[0]
            })
        self.records = records

        # <resumptionToken completeListSize="4829" cursor="50">lr~urealSamling42~~~marcxchange~50:48634</resumptionToken>
        rs = root.xpath('oai:ListRecords/oai:resumptionToken')[0]
        print rs
        self.resumption_token = rs.text()
        print 'Completed %s / %s' % (rs.attr('cursor'), rs.attr('completeListSize'))
        if self.resumption_token == '':
            self.resumption_token = None


class XmlNodeList(object):

    def __init__(self, parser, namespaces, nodes):
        self.parser = parser
        self.namespaces = namespaces
        self.nodes = nodes

    def __iter__(self):
        for node in self.nodes:
            yield XmlNode(self.parser, self.namespaces, node)

    def __getitem__(self, index):
        return XmlNode(self.parser, self.namespaces, self.nodes[index])


class XmlNode(object):

    def __init__(self, parser, namespaces, node):
        self.parser = parser
        self.namespaces = namespaces
        self.node = node

    def __repr__(self):
        if (type(self.node) == list):
            return 'list node: %d' % len(self.node)
        else:
            return 'single node'

    def attr(self, key):
        return self.node.get(key)

    def xpath(self, query):
        x = self.node.xpath(query, namespaces=self.namespaces)
        if type(x) == list:
            if len(x) == 0:
                return None
            else:
                return XmlNodeList(self.parser, self.namespaces, x)
        else:
            return XmlNode(self.parser, self.namespaces, x)

    def text(self, query=None):
        """
        convenience method to get the text value of the first matching node, or an empty string if not found
        """
        if query is None:
            return self.node.text
        else:
            n = self.node.xpath(query, namespaces=self.namespaces)
            if len(n) == 0:
                return ''
            else:
                return n[0].text


class XmlReader(object):

    def __init__(self, namespaces):
        self.parser = etree.XMLParser()
        self.namespaces = namespaces

    def parse(self, data):
        #print "START: " + str(datetime.datetime.now())
        dom = etree.fromstring(data, self.parser)
        # dom = etree.parse(file, parser)
        # diag = self.x(dom, '//srw:diagnostics')
        # if diag:
        #     msg = diag[0].xpath('//d:message',
        #                         namespaces={'d': diag[0].nsmap[None]}
        #                         )[0].text
        #     raise StandardError(msg)

        return XmlNode(self.parser, self.namespaces, dom)

    def read_file(self, filename):
        f = open(filename, mode='r')
        data = f.read()
        f.close()
        logger.debug('Read %s', filename)
        return self.parse(data)
