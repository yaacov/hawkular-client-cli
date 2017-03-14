# hawkular-client-cli

This repository includes a Python client script to access Hawkular metrics remotely.

## Introduction

Utility script for accessing Hawkular metrics server remotely, the script can query
a list of metric definitions and tags, update metrics tags, read and write metric data.
The script is using the python [hawkular-client](https://github.com/hawkular/hawkular-client-python) module.

## License and copyright

```
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
```

## Installation

To install, run ``python setup.py install`` if you installed from source code, or ``pip install hawkular-client-cli`` if using pip.

## Usage

The `-h` flag will print out a help text, that list the command line arguments.

```bash
hawkular-cli -h

usage: hawkular-cli [-h] [-U URL] [-i] [-t TENANT] [-c [CONFIG_FILE]]
                           [-p [PASSWORD]] [-T [TOKEN]] [-u [USERNAME]]
                           [-a [TAG=VALUE [TAG=VALUE ...]]]
                           [-k [KEY [KEY ...]]] [-l] [-r]
                           [-m {gauge,counter,string,availability}]
                           [-s [START]] [-e [END]] [-b [BUCKETDURATION]]
                           [--limit [LIMIT]] [-V] [--status] [--triggers] [-N]
                           [-v]
                           [KEY=VALUE [KEY=VALUE ...]]

Read/Write data to and from a Hawkular metric server.

positional arguments:
  KEY=VALUE             key value pairs to send

optional arguments:
  -h, --help            show this help message and exit
  -U URL, --url URL     Hawkualr server url
  -i, --insecure        allow insecure ssl connection
  -t TENANT, --tenant TENANT
                        Hawkualr tenenat name
  -c [CONFIG_FILE], --config [CONFIG_FILE]
                        Configurations file path
  -p [PASSWORD], --password [PASSWORD]
                        Hawkualr server password
  -T [TOKEN], --token [TOKEN]
                        Hawkualr server token
  -u [USERNAME], --username [USERNAME]
                        Hawkualr server username
  -a [TAG=VALUE [TAG=VALUE ...]], --tags [TAG=VALUE [TAG=VALUE ...]]
                        a list of tags [ when used with a list of keys, will
                        update tags for this keys ]
  -k [KEY [KEY ...]], --keys [KEY [KEY ...]]
                        a list of keys [ when used with a list of tags, will
                        update tags for this keys ]
  -l, --list            list all registered keys, can be used with --tags
                        argument for filtering
  -r, --read            read data for keys or tag list [requires the --keys or
                        --tags arguments]
  -m {gauge,counter,string,availability}, --metric {gauge,counter,string,availability}
                        use specific metrics type [gauge, counter, string,
                        availability]
  -s [START], --start [START]
                        the start date for metrics reading
  -e [END], --end [END]
                        the end date for metrics reading
  -b [BUCKETDURATION], --bucketDuration [BUCKETDURATION]
                        the metrics atatistics reading bucket duration in
                        secondes
  --limit [LIMIT]       limit for metrics reading
  -V, --verbose         be more verbose
  --status              query hawkular status
  --triggers            query hawkular alert triggers
  -N, --no-autotags     do not update tags using the config file
  -v, --version         print version

```
### Querying metric definitions [ --list ]
Metric definitions list can also be filtered using tags.

```bash
hawkular-cli --list
hawkular-cli --list --tags issue=42
```

### Querying alert triggers [ --triggers ]
Display alert triggers list (Requires hawkular-client-python >= 0.4.5).

```bash
hawkular-cli --triggers
```

### Querying metric data [ --read [--keys KEY] [--tags TAG=VALUE] ]
Query for metrics data can be done using a list of keys [ using the -keys argument ]
or using a list of tag,value pairs [ using the --tags argument ]

```bash
hawkular-cli --read --keys machine/example.com/memory.usage
hawkular-cli --read --tags issue=42
```

### Pushing new values [ KEY=VALUE ]
When pushing new data, we also update the tag values of the keys we push data to,
If not explicit tags are defined ( e.g. using the --tags argument ) tags are set using
rules in the config file.

```bash
hawkular-cli machine/example.com/memory.usage=300
```

### Modifying metric definition tags [ --keys KEY --tags TAG=VALUE ]
If a key match an auto-tagging rule from a config file, the tag value defined
in the config file will be updated. Explicit tag values defined using the command line
argument [ --tags ] will override tag values defined by rules in the config file.

```bash
hawkular-cli --keys machine/example.com/memory.usage --tags units=bytes
```

### Config file
If present, a yaml config file, can be used to store credentials information, and
tagging rules. Command line arguments will override credentials and tags defined in
the config file.

Default path for the config file is `/etc/hawkular-client-cli/conifg.yaml`

The hawkuklar part of the yaml file can store information about the hawklar server,
for example, username and password.

The auto-tagging rules match the rules regex with pre-defined tags, for example, the rules
in this example will add the tag `units` with value `bytes` to any key that match the regex pattern `.*memory.*`.

#### Using key and password
```yaml
hawkular:
  url: https://hawkular-metrics.com:443
  username: hawkular
  password: secret
  tenant: _ops
rules:
  - regex: .*memory.*
    tags:
      units: byte
  - regex: .*cpu.*
    tags:
      units: cpu
```

#### using a token
```yaml
hawkular:
  url: https://hawkular-metrics.com:443
  token: secret
  tenant: _ops
  insecure: False
rules:
  - regex: .*
    tags:
      type: node
      hostname: example.com
```

### Environment variables
If present, environment variables, can be used to store credentials information. Command line arguments and config file settings, will override credentials defined in environment variables.

```bash
# supported vars
# HAWKULAR_URL, HAWKULAR_TENANT, HAWKULAR_TOKEN, HAWKULAR_USERNAME and HAWKULAR_PASSWORD

export HAWKULAR_URL=https://example.com:8443
export HAWKULAR_TENANT=_system
export HAWKULAR_TOKEN=some.secret
hawkular-client-cli -l
```
