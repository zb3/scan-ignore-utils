import sys
import csv
import argparse

from util import *

"""
* This tool always produces a whitelist, since the DB doesn't map every IP address to a country. So if you want to exclude ranges from one country, you will also need to exclude all unknown ranges, otherwise your exclusion may not be effective.
"""

parser = argparse.ArgumentParser()
parser.add_argument('blocks_file',  help='CSV file containing IP to country id mappings')
parser.add_argument('locations_file',  help='CSV file containing country id to country code mappings')
parser.add_argument('CC', nargs='+', help='country code')
parser.add_argument('-b', action='store_true', help='Negate the countries list.')
parser.add_argument('-n', action='store_true', help="Don't use CIDR format for output")
args = parser.parse_args()

no_cidr = args.n
blacklist_mode = args.b
target_countries = [cc.lower() for cc in args.CC]

countries = []
country_map = {}
ranges = []

with open(args.locations_file, newline='', encoding='utf-8') as csvfile:
  dbreader = csv.reader(csvfile)
  next(dbreader)

  for row in dbreader:
    cc = row[4].lower()
    if cc:
      countries.append(cc)

    country_map[row[0]] = cc


with open(args.blocks_file, newline='', encoding='utf-8') as csvfile:
  dbreader = csv.reader(csvfile)
  next(dbreader)

  for row in dbreader:
    block, cid = row[:2]
    cc = country_map.get(cid)
    if not cc:
      continue

    cc_there = cc in target_countries

    if blacklist_mode != cc_there:
      ranges.append(ip_range(block))


ranges = merge_ranges(ranges)
total = ranges_total(ranges)

for line in output_ranges(ranges, no_cidr):
  print(line)

print('%d addresses in output ranges' % total, file=sys.stderr)
