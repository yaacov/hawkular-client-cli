"""
    Copyright 2016 Red Hat, Inc. and/or its affiliates
    and other contributors.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import sys
import re
import ssl
import argparse
import yaml
from datetime import datetime
from future.moves.urllib.parse import urlparse
from hawkular.metrics import HawkularMetricsClient, MetricType

_VERSION = '0.8.1'
_DESCRIPTION = 'Read/Write data to and from a Hawkular metric server.'

class CommandLine(object):
    def __init__(self):
        self._get_args()
        self._get_config()
        self._get_args()
        self._get_client()

    def log(self, *args):
        """ Pring logs
        """
        if self.args.verbose:
            print(*args)

    # Read cli arguments
    def _get_args(self):
        """ Get and parse command lint arguments
        """
        parser = argparse.ArgumentParser(description=_DESCRIPTION)
        parser.add_argument('--url', dest='url', type=str,
                            help='Hawkualr server url')
        parser.add_argument('-i', '--insecure', action='store_true',
                            help='allow insecure ssl connection')
        parser.add_argument('-t', '--tenant', metavar='NAME', type=str,
                            help='Hawkualr tenenat name')
        parser.add_argument('-c', '--config', dest='config_file', type=str, nargs='?',
                            default='/etc/hawkular-client-cli/conifg.yaml',
                            help='Configurations file path')
        parser.add_argument('-p', '--password', dest='password', type=str, nargs='?',
                            help='Hawkualr server password')
        parser.add_argument('-u', '--username', dest='username', type=str, nargs='?',
                            help='Hawkualr server username')
        parser.add_argument('values', metavar='KEY=VALUE', type=str, nargs='*',
                            help='key value pairs to send')
        parser.add_argument('-a', '--tags', metavar='TAG=VALUE', dest='tags', type=str, nargs='*',
                            help='a list of tags [ when used with a list of keys, will update tags for this keys ]')
        parser.add_argument('-k', '--keys', metavar='KEY', dest='keys', type=str, nargs='*',
                            help='a list of keys [ when used with a list of tags, will update tags for this keys ]')
        parser.add_argument('-l', '--list', action='store_true',
                            help='list all registered keys, can be used with --tags argument for filtering')
        parser.add_argument('-r', '--read', action='store_true',
                            help='read data for keys or tag list [requires the --keys or --tags arguments]')
        parser.add_argument('-V', '--verbose', action='store_true',
                            help='be more verbose')
        parser.add_argument('-v', '--version', action='store_true',
                            help='print version')
        args = parser.parse_args()

        if args.version:
            print('hawkular-client-cli v' + _VERSION + '\n')
            sys.exit(1)

        self.parser = parser
        self.args = args

    # Read config file
    def _get_config(self):
        """ Get and parse config file parameters
        """
        config = {}
        if os.path.exists(self.args.config_file):
            self.log('Reading config file', self.args.config_file)
            config = yaml.load(file(self.args.config_file))
        config['hawkular'] = config.get('hawkular', {})
        config['tags'] = config.get('tags', [])

        self.config = config

    # Get Hawkular server and credentials
    def _get_client(self):
        """ Create a Hawkular metrics client
        """
        url = self.args.url or self.config.get('hawkular').get('url') or None
        tenant = self.args.tenant or self.config.get('hawkular').get('tenant') or None
        username = self.args.username or self.config.get('hawkular').get('username') or None
        password = self.args.password or self.config.get('hawkular').get('password') or None
        context = ssl._create_unverified_context() if self.args.insecure else None

        if not url:
            print('Error: missing url\n')
            self.parser.print_help()
            sys.exit(1)
        if not tenant:
            print('Error: missing tenant\n')
            self.parser.print_help()
            sys.exit(1)
        if not username:
            print('Error: missing username\n')
            self.parser.print_help()
            sys.exit(1)
        if not password:
            print('Error: missing password\n')
            self.parser.print_help()
            sys.exit(1)

        try:
            url_args = urlparse(url)
            client = HawkularMetricsClient(host=url_args.hostname, port=url_args.port,
                                           scheme=url_args.scheme, username=username, password=password,
                                           tenant_id=tenant, context=context)
            self.log('Connectd:', url_args.hostname, tenant, url_args.scheme, url_args.hostname, url_args.port)
        except Exception as err:
            print('[ERROR] Not Connectd:', url_args.hostname, tenant, url_args.scheme, url_args.hostname, url_args.port)
            print(err, '\n')
            self.parser.print_help()
            sys.exit(1)

        self.client = client

    def _query_metric_definitions(self):
        """ Get a list of metric definitions
        """
        tags = dict([i.split("=")[0], i.split("=")[1]] for i in self.args.tags) if self.args.tags else {}
        definitions = self.client.query_metric_definitions(**tags)
        for definition in definitions:
            print('key: ', definition.get('id'))
            print('tags:', definition.get('tags') or {})
            print()

    def _query_metric_by_keys(self):
        """ get meric data
        """
        for key in self.args.keys:
            print('key:', key)
            values = self.client.query_metric(MetricType.Gauge, key, limit=10)
            print('values:')
            for value in values:
                timestamp = value.get('timestamp')
                timestr = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print ('    ', timestamp, '(', timestr, ')', value.get('value'))
            print()

    def _query_metric_by_tags(self):
        """ Get meric data
        """
        tags = dict([i.split("=")[0], i.split("=")[1]] for i in self.args.tags) if self.args.tags else {}
        definitions = self.client.query_metric_definitions(**tags)
        for definition in definitions:
            key = definition.get('id')
            print('key:', key)
            values = self.client.query_metric(MetricType.Gauge, key, limit=3)
            print('values:')
            for value in values:
                timestamp = value.get('timestamp')
                timestr = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print ('    ', timestamp, '(', timestr, ')', value.get('value'))
            print()

    def _push(self):
        """ Push meric data
        """
        for pair in self.args.values:
            key, value = pair.split("=")
            self.log('Push:', key, float(value))
            self.client.push(MetricType.Gauge, key, float(value))

    def _update_metric_tags(self):
        """ Update metric tags
        """
        # Get tags from command line args
        tags = dict([i.split("=")[0], i.split("=")[1]] for i in self.args.tags) if self.args.tags else {}
        # Get tags rules from the config file
        rules = self.config.get('rules') or []

        for pair in self.args.values:
            key = pair.split("=")[0]
            # Clean the tags for this key
            key_tags = {}

            # Check all tagging rules, and use the rules that apply for this key
            for rule in rules:
                compiled_rule = re.compile(rule.get('regex'))
                if compiled_rule.match(key):
                    key_tags.update(rule.get('tags') or {})
            key_tags.update(tags)

            # Update tags in Hawkular
            if key_tags != {}:
                self.log('Update:', key, key_tags)
                self.client.update_metric_tags(MetricType.Gauge, key, **key_tags)

    def _update_metric_tags_by_keys(self):
        """ Update metric tags
        """
        # Get tags from command line args
        tags = dict([i.split("=")[0], i.split("=")[1]] for i in self.args.tags) if self.args.tags else {}
        # Get tags rules from the config file
        rules = self.config.get('rules') or []

        for key in self.args.keys:
            # Clean the tags for this key
            key_tags = {}

            # Check all tagging rules, and use the rules that apply for this key
            for rule in rules:
                compiled_rule = re.compile(rule.get('regex'))
                if compiled_rule.match(key):
                    key_tags.update(rule.get('tags') or {})
            key_tags.update(tags)

            # Update tags in Hawkular
            if key_tags != {}:
                self.log('Update:', key, key_tags)
                self.client.update_metric_tags(MetricType.Gauge, key, **key_tags)

    def run(self):
        """ Run the command line actions
        """
        # Do actions list
        if self.args.list:
            self.log('List keys by tags:', self.args.tags)
            try:
                self._query_metric_definitions()
            except Exception as err:
                print(err, '\n')
                sys.exit(1)

        # Do actions read keys
        if self.args.read and self.args.keys:
            self.log('Read metrics values by keys:')
            try:
                self._query_metric_by_keys()
            except Exception as err:
                print(err, '\n')
                sys.exit(1)

        # Do actions read keys
        if self.args.read and self.args.tags:
            self.log('Read metrics values by tags:', self.args.tags)
            try:
                self._query_metric_by_tags()
            except Exception as err:
                print(err, '\n')
                sys.exit(1)

        # Do actions send key value pairs
        if self.args.values:
            self.log('Push metrics values by key=value pairs:', self.args.values)
            try:
                self._push()
            except Exception as err:
                print(err, '\n')
                sys.exit(1)

            # Update tags for the key=values pairs
            try:
                self._update_metric_tags()
            except Exception as err:
                print(err, '\n')
                sys.exit(1)

        # Do actions update tags
        if self.args.keys and self.args.tags:
            self.log('Update metrics tags by tag=value pairs:')
            try:
                self._update_metric_tags_by_keys()
            except Exception as err:
                print(err, '\n')
                sys.exit(1)

def main():
    coammand_line = CommandLine()
    coammand_line.run()

if __name__ == "__main__":
    main()
