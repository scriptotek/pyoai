import datetime
from oai import OaiClient


def write_xml_file(data, filename):
    """ Writes raw records to disk """

    f = open(filename, mode='w')
    f.write(data.encode('utf-8'))
    f.close()
    print 'Wrote %s' % filename


# Range limits are inclusive:
#  from specifies a bound that must be interpreted as "greater than or equal to",
#  until specifies a bound that must be interpreted as "less than or equal to".
# legitimate formats are YYYY-MM-DD and YYYY-MM-DDThh:mm:ssZ

repo = 'http://data.libris.kb.se/authorities/oaipmh'
set_spec = 'type:S'

repo = 'http://oai.bibsys.no/oai/repository'
set_spec = 'BIBSYS_complete'

cli = OaiClient(repo)
cli.help()
cli.set_format('info:lc/xmlns/marcxchange-v1')

date_from = cli.identify['earliestDatestamp']
now = datetime.datetime.now()
if cli.identify['granularity'] == 'YYYY-MM-DDThh:mm:ssZ':
    date_until = now.strftime('%Y-%m-%dT23:59:59Z')
else:
    date_until = now.strftime('%Y-%m-%d')

n = 0
for response in cli.harvest(set_spec, date_from, date_until):
    n += 1
    print '[%05d] Got %d records' % (n, len(response.records))
    write_xml_file(response.raw_response, 'data/response%05d.xml' % n)
    print "ok, sleep 2 secs"
    #time.sleep(2)
