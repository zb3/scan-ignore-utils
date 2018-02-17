# scan-ignore-utils

This repo contains the `exclude.conf` file for `masscan` which I use as an input to `ignore-networks` tool which ignores networks based on their name.

Contents of that file are arbitrary, I ignore networks I want to, but the `ignore-networks` tool is universal, because you can specify what you want to ignore.

You can also take the opposite approach and use the `include-networks` tool to generate a list of hosts to include based on AS name patterns.

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
