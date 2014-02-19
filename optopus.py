from argparse import ArgumentParser
from fabric.api import hosts
from fabric.tasks import Task
from getpass import getpass
import fabric.api
import json
import os
import sys
import urllib2

class FabWrapper(Task):
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs
        self.name = 'Optopus CLI Task'

    def run(self):
        self.func(**self.kwargs)

class Client(object):
    def __init__(self, endpoint, dry_run=False):
        self._endpoint = endpoint
        self._dry_run = dry_run

    def search(self, string, types=None):
        path = "/api/search?string=%s" % urllib2.quote(string)
        if types:
            path += "&types=%s" % ','.join(types)
        return self._get(path)['results']

    def get_children(self, hostname):
        path = "/api/node/%s/children" % hostname
        return self._get(path)['children']

    def _get(self, path):
        req = urllib2.Request("%s%s" % (self._endpoint, path))
        req.add_header('Accept', 'application/json')
        req.add_header('User-agent', 'optopus-cli/0.1')
        if self._dry_run:
            results = req.get_full_url()
        else:
            url = urllib2.urlopen(req)
            results = json.loads(url.read())
        return results

class CLI(object):
    @classmethod
    def run(class_):
        class_.parse_args()
        class_.client = Client(class_.args.optopus_endpoint, class_.args.show_url)
        sys.exit(class_.args.func(class_.args))

    @classmethod
    def search(class_, args):
        types = ['node', 'hypervisor', 'network_node']
        query_string = ' '.join(args.query)
        results = class_.client.search(query_string, types)
        if args.show_url:
            print results
            sys.exit(0)
        if class_.check_args_for_fabric():
            class_.execute_fabric(class_.get_hosts(results))
        else:
            class_.display_hosts(results)
        return 0

    @classmethod
    def get_children(class_, args):
        for child in class_.client.get_children(args.hostname):
            print child
        return 0

    @classmethod
    def execute_fabric(class_, hosts):
        if class_.args.run:
            fab_method = fabric.operations.run
            fab_kwargs = { 'command': ' '.join(class_.args.run), 'warn_only': True }
        elif class_.args.sudo:
            fab_method = fabric.operations.sudo
            fab_kwargs = { 'command': ' '.join(class_.args.sudo), 'warn_only': True }
        elif class_.args.get:
            fab_method = fabric.operations.get
            fab_kwargs = { 'remote_path': class_.args.get }
        elif class_.args.put:
            (local_path, remote_path) = class_.args.put
            fab_method = fabric.operations.put
            fab_kwargs = { 'local_path': local_path, 'remote_path': remote_path }

        settings = { 'user': class_.args.fab_user }
        if class_.args.parallel:
            settings['parallel'] = True
            settings['password'] = getpass("Login password for '%s': " % class_.args.fab_user)

        with fabric.context_managers.settings(**settings):
            task = FabWrapper(fab_method, **fab_kwargs)
            fabric.tasks.execute(task, hosts=hosts)

    @classmethod
    def check_args_for_fabric(class_):
        if class_.args.run or class_.args.sudo \
            or class_.args.get or class_.args.put:
                return True
        else:
            return False

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
            if class_.args.show_properties:
                for prop in class_.args.show_properties:
                    print "%15s: %s" % (prop, item.get(prop, ''))
            if class_.args.show_facts:
                for fact in class_.args.show_facts:
                    print "%15s: %s" % (fact, item['facts'].get(fact, ''))
                print ''

    @classmethod
    def parse_args(class_):
        parsers = {}
        parser = ArgumentParser(description='Search the optopus api and perform various actions')
        parser.add_argument('-e', '--optopus-endpoint', default=os.environ.get('OPTOPUS_ENDPOINT', None))
        parser.add_argument('--show-url', action='store_true', default=False, help="Return the optopus url that will be called and exit")
        subparsers = parser.add_subparsers(title='subcommands')

        parsers['search'] = subparsers.add_parser('search')
        parsers['search'].set_defaults(func=class_.search)
        parsers['search'].add_argument('query', metavar='QUERY', nargs='+', help="Query for nodes, this can take any elasticsearch parameters compatble with a search string")
        parsers['search'].add_argument('-sF', '--show-facts', nargs='+', metavar='FACT', help="Show facts about the resulting nodes")
        parsers['search'].add_argument('-sP', '--show-properties', nargs='+', metavar='PROPERTY', help="Show properties about the resulting nodes")
        parsers['search'].add_argument('--run', metavar='SHELL', nargs='+', help="Run a shell command against the resulting hosts")
        parsers['search'].add_argument('--sudo', metavar='SHELL', nargs='+', help="Run a shell command using sudo against the resulting hosts")
        parsers['search'].add_argument('--get', metavar='REMOTE_PATH', help="Pull down remote files from resulting hosts")
        parsers['search'].add_argument('--put', metavar='LOCAL_PATH REMOTE_PATH', nargs=2, help="Upload LOCAL_PATH to REMOTE_PATH")
        parsers['search'].add_argument('--fab-user', metavar='USER', default=os.environ.get('FAB_USER', os.environ.get('USER')), help="When invoking Fabric, use this user to run shell commands")
        parsers['search'].add_argument('-p', '--parallel', action='store_true', default=False, help="Run ssh commands in parallel")

        parsers['get-children'] = subparsers.add_parser('get-children')
        parsers['get-children'].add_argument('hostname', metavar='HOSTNAME', help="Show children for the supplied hostname")
        parsers['get-children'].set_defaults(func=class_.get_children)

        class_.args = parser.parse_args()

