# scan-ignore-utils

This repo contains the `exclude.conf` file for `masscan` which I use as an input to the `ignore-networks` tool which ignores networks based on their name.

Contents of that file are arbitrary, I ignore networks I want to, but the `ignore-networks` tool is universal, because you can specify what you want to ignore.

You can also take the opposite approach and use the `include-networks` tool to generate a list of hosts to include based on AS name patterns.

There are more tools here, see below.

## ignore-networks

This is a PoC experimental tool to generate ignore files for `masscan`/`ZMap` based on AS names. It can be used to ignore addresses wasted by the US government, Universities and also unreachable addresses...

This can also merge the results with existing ignore files.

The tool does not produce exact results with default settings, because it skips small ranges. In some cases, "good" addresses are ignored, and bad are not. This is to prevent `ignore-networks` from producing too many small ignored ranges, but it can be turned off easily.


## include-networks

Is just like the above except the obvious difference, but it's also much simpler and more exact.

**Note** however that this tool obviously can't produce high quality results if the input database contains inexact data, and this is probably the case when using `Geolite2`. More exact methods to find ranges may exist (for instance `Google`, `Amazon` and  `Microsoft` provide downloadable lists of their IP ranges)


## Usage....

In order to use tools listed above you **must** first obtain the `GeoLite2 ASN` database in CSV format (`CIDR,ASN,AS Name`). You can obtain this file for free here: [link](http://dev.maxmind.com/geoip/geoip2/geolite2/)

Network names to ignore/include are specified in Python files (default is `config.py`) that contain `ignore_patterns` (used by `ignore-networks.py`) or/and `include_patterns` (used by `include-networks.py`) variables, specifying a list of patterns which are then passed to `re.compile`.

`ignore-networks.py` always ignores unallocated ranges even if no networks specified.

You can run these tools this way:
```
python3 ignore-networks.py [-c configfile] csvdbfile outfile [existing ignore files]
python3 include-networks.py [-c configfile] csvdbfile outfile [existing include files]
```

Configs included: (oh look - a table!)

|   | ignore-networks.py | include-networks.py |
| - | - | - |
| config.py | US Goverment, Universities/Education, NERNs, CDNs, Hosting/Cloud providers | Cloud providers | 
| config_hostcloud.py | same as above except Hosting/Cloud providers | Hosting/Cloud providers |

There are more options, but for those you will need to... read and modify the source :)

## country-ranges.py
This tool can export all networks for a given (possibly negated) set of countries. To use it you **must** first obtain `GeoLite2 Country` database in CSV format. You'll need two files, one for mapping networks to country ids (`GeoLite2-Country-Blocks-IPv4.csv`), and the second mapping country ids to country codes (`GeoLite2-Country-Locations-en.csv`).

```
$ python country-ranges.py blocks_file locations_file US CA NL BR
```
Output is in CIDR format unless `-n` used.

This tool **always** produces a whitelist. Using the output as a blacklist may not be effective, since the DB doesn't cover the whole IPv4 space. If you want to blacklist networks from a set of countries, you can negate the set using the `-b` flag:
```
$ python country-ranges.py -b US CN
```

The output of that command will include all networks with countries other than those specified, but it will **not** include networks with no country mapping in the DB.


## invert-ranges.py
Operates on standard input/output and does what it's name suggests. It outputs ranges in CIDR format unless `-n` used.
```
$ echo '16.0.0.0/4' | python invert-ranges.py
0.0.0.0/4
32.0.0.0/3
64.0.0.0/2
128.0.0.0/1

$ echo '16.0.0.0/4' | python invert-ranges.py -n
0.0.0.0-15.255.255.255
32.0.0.0-255.255.255.255
```

## largest-networks.py
This tool displays AS names that have the most IPv4 addresses (with their address count). This requires the `GeoLite2 ASN` csv file to be passed as the first argument. The second argument decides how much items to display.
```
$ python largest-networks.py db.csv 4
106924288 No.31,Jin-rong Street
81752832 AT&T Services, Inc.
71822336 Comcast Cable Communications, LLC
66012160 DoD Network Information Center
```
use `-a` to also display their ASNs:
```
$ python largest-networks.py -a db.csv 2
106924288 No.31,Jin-rong Street 4134
81752832 AT&T Services, Inc. 11712,5731,397958,397665,4466,4468,7018,397910,5728,797,397977,4465,397872,397762,13979,397757

```
