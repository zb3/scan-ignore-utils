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

In order to use it you **must** first obtain the `GeoLite2 ASN` database in CSV format (`CIDR,ASN,AS Name`). You can obtain this file for free here: [link](http://dev.maxmind.com/geoip/geoip2/geolite2/)

Then you can adjust what to ignore/include in the `config.py` file, which should contain at least `ignore_pattenrs` and `include_patterns` variables with lists of patterns that will then be passed to `re.compile`.

You can run these tools this way:
```
python3 ignore-networks.py [csvdbfile] [outfile] [existing ignore files]
python3 include-networks.py [csvdbfile] [outfile] [existing include files]
```

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
