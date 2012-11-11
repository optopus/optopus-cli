from argparse import ArgumentParser
from fabric.api import hosts
from fabric.tasks import Task
import fabric.api
import json
import os
import sys
import urllib2

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
        if class_.args.run or class_.args.sudo:
            if class_.args.run:
                fab_method = fabric.operations.run
                fab_args = ' '.join(class_.args.run)
            else:
                fab_method = fabric.operations.sudo
                fab_args = ' '.join(class_.args.sudo)

            for host in class_.get_hosts(results):
                settings = { 'user': class_.args.fab_user, 'host_string': host }
                with fabric.context_managers.settings(**settings):
                    fab_method(fab_args)
        else:
            class_.display_hosts(results)

    @classmethod
    def get_fab_settings(class_, host_list):
        return { 'user': class_.args.fab_user }

    @classmethod
    def get_hosts(class_, results):
        hosts = []
        for item in results:
            hosts.append(item['hostname'])
        return hosts

    @classmethod
    def display_hosts(class_, results):
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
        parser.add_argument('--run', metavar='SHELL', nargs='+', help="Run a shell command against the resulting hosts")
        parser.add_argument('--sudo', metavar='SHELL', nargs='+', help="Run a shell command using sudo against the resulting hosts")
        parser.add_argument('--fab-user', metavar='USER', default=os.environ.get('FAB_USER', os.environ.get('USER')), help="When invoking Fabric, use this user to run shell commands")
        class_.args = parser.parse_args()

