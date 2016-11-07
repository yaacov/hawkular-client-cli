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
from builtins import *

import os
import sys
import re
import ssl
import argparse
import yaml
import ssl
from future.moves.urllib.parse import urlparse
from hawkular.metrics import HawkularMetricsClient, MetricType

_VERSION = '0.4.0'
parser = argparse.ArgumentParser(description='Read/Write data to and from a Hawkular metric server.')

# Read cli arguments
def _get_args():
    """Get and parse command lint arguments
    """
    parser.add_argument('-n', '--url', dest='url', type=str, nargs='?',
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
        help='a list of tags')
    parser.add_argument('-k', '--keys', metavar='KEY', dest='keys', type=str, nargs='*',
        help='a list of keys')
    parser.add_argument('-l', '--list', action='store_true',
        help='list all registered keys, can be used with --tags argument for filtering')
    parser.add_argument('-r', '--read', action='store_true',
        help='read data for keys or tag list [requires the --keys or --tags arguments]')
    parser.add_argument('-v', '--version', action='store_true',
        help='print version')
    args = parser.parse_args()

    if args.version:
        print('hawkular-client-cli v' + _VERSION + '\n')
        sys.exit(1)

    return args

# Read config file
def _get_config(config_file):
    """ Get and parse config file parameters
    """
    config = {}
    if os.path.exists(config_file):
        config = yaml.load(file(config_file))
    config['hawkular'] = config.get('hawkular', {})
    config['tags'] = config.get('tags', [])

    return config

# Get Hawkular server and credentials
def _get_client(args, config):
    """ Create a Hawkular metrics client
    """
    url = args.url or config.get('hawkular').get('url') or None
    tenant = args.tenant or config.get('hawkular').get('tenant') or None
    username = args.username or config.get('hawkular').get('username') or None
    password = args.password or config.get('hawkular').get('password') or None
    context = ssl._create_unverified_context() if args.insecure else None

    if not url:
        print('Error: missing url\n')
        parser.print_help()
        sys.exit(1)
    if not tenant:
        print('Error: missing tenant\n')
        parser.print_help()
        sys.exit(1)
    if not username:
        print('Error: missing username\n')
        parser.print_help()
        sys.exit(1)
    if not password:
        print('Error: missing password\n')
        parser.print_help()
        sys.exit(1)

    try:
        url_args = urlparse(url)
        client = HawkularMetricsClient(host=url_args.hostname, port=url_args.port,
            scheme=url_args.scheme, username=username, password=password,
            tenant_id=tenant, context=context)
    except Exception as err:
        print(err, '\n')
        parser.print_help()
        sys.exit(1)

    return client

def _query_metric_definitions(client, args, config):
    """ get a list of metric definitions
    """
    tags = dict([i.split("=")[0], i.split("=")[1]] for i in args.tags) if args.tags else {}
    definitions = client.query_metric_definitions(**tags)
    for definition in definitions:
        print('key: ', definition.get('id'))
        print('tags:', definition.get('tags') or {})
        print()

def _query_metric_by_keys(client, args, config):
    """ get meric data
    """
    for key in args.keys:
        print('key:', key)
        values = client.query_metric(MetricType.Gauge, key, limit=10)
        print('values:')
        for v in values:
            print ('    ', v.get('timestamp'), v.get('value'))
        print()

def _query_metric_by_tags(client, args, config):
    """ get meric data
    """
    tags = dict([i.split("=")[0], i.split("=")[1]] for i in args.tags) if args.tags else {}
    definitions = client.query_metric_definitions(**tags)
    for definition in definitions:
        key = definition.get('id')
        print('key:', key)
        values = client.query_metric(MetricType.Gauge, key, limit=3)
        print('values:')
        for v in values:
            print ('    ', v.get('timestamp'), v.get('value'))
        print()

def _push(client, args, config):
    """ push meric data
    """
    for pair in args.values:
        key, value = pair.split("=")
        client.push(MetricType.Gauge, key, float(value))

def _update_metric_tags(client, args, config):
    """ update metric tags
    """
    # Get tags from command line args
    tags = dict([i.split("=")[0], i.split("=")[1]] for i in args.tags) if args.tags else {}
    # Get tags rules from the config file
    rules = config.get('rules') or []

    for pair in args.values:
        key, value = pair.split("=")
        # Clean the tags for this key
        key_tags = {}

        # Check all tagging rules, and use the rules that apply for this key
        for rule in rules:
            compiled_rule = re.compile(rule.get('regex'))
            if compiled_rule.match(key):
                key_tags.update(rule.get('tags') or {})
        key_tags.update(tags)

        # Update tags in Hawkular
        client.update_metric_tags(MetricType.Gauge, key, **key_tags)

def _update_metric_tags_by_keys(client, args, config):
    """ update metric tags
    """
    # Get tags from command line args
    tags = dict([i.split("=")[0], i.split("=")[1]] for i in args.tags) if args.tags else {}
    # Get tags rules from the config file
    rules = config.get('rules') or []

    for key in args.keys:
        # Clean the tags for this key
        key_tags = {}

        # Check all tagging rules, and use the rules that apply for this key
        for rule in rules:
            compiled_rule = re.compile(rule.get('regex'))
            if compiled_rule.match(key):
                key_tags.update(rule.get('tags') or {})
        key_tags.update(tags)

        # Update tags in Hawkular
        client.update_metric_tags(MetricType.Gauge, key, **key_tags)

def main():
    # Get client, config and args
    args = _get_args()
    config = _get_config(args.config_file)
    client = _get_client(args, config)

    # Do actions list
    if args.list:
        try:
            _query_metric_definitions(client, args, config)
        except Exception as err:
            print(err, '\n')
            sys.exit(1)

    # Do actions read keys
    if args.read and args.keys:
        try:
            _query_metric_by_keys(client, args, config)
        except Exception as err:
            print(err, '\n')
            sys.exit(1)

    # Do actions read keys
    if args.read and args.tags:
        try:
            _query_metric_by_tags(client, args, config)
        except Exception as err:
            print(err, '\n')
            sys.exit(1)

    # Do actions send key value pairs
    if args.values:
        try:
            _push(client, args, config)
        except Exception as err:
            print(err, '\n')
            sys.exit(1)

        # Update tags for the key=values pairs
        try:
            _update_metric_tags(client, args, config)
        except Exception as err:
            print(err, '\n')
            sys.exit(1)

    # Do actions update tags
    if args.keys and args.tags:
        try:
            _update_metric_tags_by_keys(client, args, config)
        except Exception as err:
            print(err, '\n')
            sys.exit(1)

if __name__ == "__main__":
    main()
