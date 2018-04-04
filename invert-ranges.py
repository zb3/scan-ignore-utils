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

total = ranges_total(new_ranges)

for line in output_ranges(new_ranges, no_cidr):
  print(line)

print('%d output ranges' % total, file=sys.stderr)