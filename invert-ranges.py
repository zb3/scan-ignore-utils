import sys

from util import *

no_cidr = '-n' in sys.argv

ranges = []

for line in sys.stdin:
  line = line.strip()

  if not line or line[0] == '#':
    continue

  r = ip_range(line)
  ranges.append(r)


ranges = merge_ranges(ranges)
new_ranges = invert_ranges(ranges)

total = 0

for start, end in new_ranges:
  total += end - start + 1

  if no_cidr:
    print(long2ip(start)+'-'+long2ip(end))
  else:
    for cidr in range_to_cidrs(start, end):
      print(cidr_to_str(cidr))

