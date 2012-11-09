import urllib2
import json
from argparse import ArgumentParser
import sys
import os

class Client(object):
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def search(self, string, types=None):
        path = "/api/search?string=%s" % urllib2.quote(string)
        if types:
            path += "&types=%s" % ','.join(types)
        return self._get(path)

    def _get(self, path):
        req = urllib2.Request("%s%s" % (self._endpoint, path))
        req.add_header('Accept', 'application/json')
        req.add_header('User-agent', 'optopus-cli/0.1')
        url = urllib2.urlopen(req)
        return json.loads(url.read())['results']

class CLI(object):
    @classmethod
    def run(class_):
        class_.parse_args()
        client = Client(class_.args.optopus_endpoint)
        types = ['node', 'hypervisor', 'network_node']
        query_string = ' '.join(class_.args.query)
        results = client.search(query_string, types)
        print class_.args.show_facts
        for item in results:
            print item['hostname']
            if class_.args.show_facts:
                for fact in class_.args.show_facts:
                    print "%15s: %s" % (fact, item['facts'].get(fact, ''))
                print ''

    @classmethod
    def parse_args(class_):
        parser = ArgumentParser(description='Search the optopus api and perform various actions')
        parser.add_argument('query', metavar='QUERY', nargs='+', help="Query for nodes, this can take any elasticsearch parameters compatble with a search string")
        parser.add_argument('-sF', '--show-facts', nargs='+', metavar='FACTS', help="Show facts about the resulting nodes. Can be comma separated for multiple facts.")
        parser.add_argument('-e', '--optopus-endpoint', default=os.environ.get('OPTOPUS_ENDPOINT', None))
        class_.args = parser.parse_args()

