# scan-ignore-utils

This repo contains the `exclude.conf` file for `masscan` which I use as an input to `ignore-networks` tool which ignores networks based on their name.

Contents of that file are arbitrary, I ignore networks I want to, but the `ignore-network` tool is universal, because you can specify what you want to ignore.

## ignore-networks

This is a PoC experimental tool to generate ignore files for `masscan`/`ZMap` based on AS names. It can be used to ignore addresses wasted by the US government, Universities and also unreachable addresses...

This can also merge the results with existing ignore files.

The tool does not produce exact results with default settings, because it skips small ranges. In some cases, "good" addresses are ignored, and bad are not. This is to prevent `ignore-networks` from producing too many small ignored ranges, but it can be turned off easily.

### Usage....

In order to use it you **must** first obtain `GeoLite2 ASN` database from `MaxMind` in csv format (`CIDR,ASN,AS Name`). You can obtain this file for free here: [link](http://dev.maxmind.com/geoip/geoip2/geolite2/)

Then... I'm sorry but there's no commandline interface. You must edit the source, but alternative'd be a config file with the same syntax anyway. Then run it like:

```
python3 ignore.py [csvdbfile] [outfile] [existing ignore files if any]
```





