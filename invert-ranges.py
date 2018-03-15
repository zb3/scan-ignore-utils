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

new_ranges = [[0, 2**32-1]]

for s, e in ranges:
  if s == new_ranges[-1][0]:
    new_ranges[-1][0] = e+1
  else:
    new_ranges[-1][1] = s-1
    
    if e < 2**32-1:
      new_ranges.append([e+1, 2**32-1])

if new_ranges[-1][0] == new_ranges[-1][1]:
  new_ranges = new_ranges[:-1]
  
total = 0

for start, end in new_ranges:
  total += end - start + 1
    
  if no_cidr:
    print(long2ip(start)+'-'+long2ip(end))
  else:
    for cidr in range_to_cidrs(start, end):
      print(cidr_to_str(cidr))
    
   