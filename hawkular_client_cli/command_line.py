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
import re
import ssl
import argparse
import yaml
import ssl
from future.moves.urllib.parse import urlparse
from hawkular.metrics import HawkularMetricsClient, MetricType

# Read cli arguments
def _get_args():
    """Get and parse command lint arguments
    """
    
    parser = argparse.ArgumentParser(description='Read/Write data to and from a Hawkular metric server.')
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
        help='a list of tags to update')
    parser.add_argument('-k', '--keys', metavar='KEY', dest='keys', type=str, nargs='*',
        help='a list of keys to update')
    parser.add_argument('-l', '--list', action='store_true',
        help='list all registered keys')
    parser.add_argument('-r', '--read', metavar='KEY', type=str, nargs='+',
        help='read data for keys')
    return parser.parse_args()

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

    url_args = urlparse(url)
    return HawkularMetricsClient(host=url_args.hostname, port=url_args.port, 
         scheme=url_args.scheme, username=username, password=password, 
         tenant_id=tenant, context=context)

def main():
    # Get client, config and args
    args = _get_args()
    config = _get_config(args.config_file)
    client = _get_client(args, config)

    # Do actions list
    if args.list:
        definitions = client.query_metric_definitions()
        for definition in definitions:
            print('id:  ', definition.get('id'))
            print('tags:', definition.get('tags') or {})
            print()

    # Do actions read keys
    if args.read:
        for key in args.read:
            print(key, )
            values = client.query_metric(MetricType.Gauge, key, limit=10)
            for v in values:
                print (v.get('timestamp'), v.get('value'))

    # Do actions send key value pairs
    if args.values:
        for pair in args.values:
            key, value = pair.split("=")
            client.push(MetricType.Gauge, key, float(value))

    # Do actions update tags
    if args.keys and args.tags:
        # Get tags from command line args
        tags = dict([i.split("=")[0], i.split("=")[1]] for i in args.tags)
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
            client.update_metric_tags(MetricType.Gauge, key, key_tags)
