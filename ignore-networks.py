import socket
import struct
import csv
import re
import io
import math
import sys
import argparse
import itertools

from runpy import run_path
from util import *


min_ignore = 1 << 14
max_good_ignore = 256
min_gap_ignore = 1 << 17
force_cidr_output = True #set to True for ZMap

## options for debug output from this script

print_matched_names = True
print_gaps_min = 1 << 17

#print max [print_small] items from good blocks smaller than [print_small_size]
print_small = 1024
print_small_size = 4


####   ####   ####
####   ####   ####
####   ####   ####

parser = argparse.ArgumentParser()
parser.add_argument('dbfile',  help='CSV file containing IP to ASN mappings')
parser.add_argument('outfile', help='Output file')
parser.add_argument('infile', nargs='*', help='Files with additional ranges to ignore')
parser.add_argument('-c', default='config.py', help='Config file containing the "ignore_patterns" array. This defaults to "config.py"')
args = parser.parse_args()

dbfile = args.dbfile
outfile = args.outfile
infiles = args.infile
cfgfile = args.c

cfgdict = run_path(cfgfile)
ignore_patterns = cfgdict['ignore_patterns']
ignore_pattern_groups = cfgdict.get('ignore_pattern_groups', [])


##

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

to_ignore = []
already_ignored = gaps_size = 0
ignored_by_us = skipped_bad = skipped_good = skipped_gaps = 0
pattern_ignored_sum = {}
pattern_matched_names = {}
pattern_map = {}

for pat in ignore_patterns:
  pc = re.compile(pat)
  pattern_map[pat] = pc
  pattern_ignored_sum[pc] = 0
  pattern_matched_names[pc] = set()
  to_ignore.append(pc)


ranges = []
last_end = -1

print('parsing...')

with open(dbfile, newline='', encoding='utf-8') as csvfile:
  dbreader = csv.reader(csvfile)

  next(dbreader)

  for block in dbreader:
    block, _, name = block

    start, end = ip_range(block)
    is_bad = False

    for pat in to_ignore:
      if pat.search(name):
        if print_matched_names:
          pattern_matched_names[pat].add(name)

        is_bad = True
        break

    if start - last_end > 1:
      ranges.append(('bad', last_end+1, start-1, 'gap', '(gap)'))

    ranges.append(('bad' if is_bad else 'good', start, end, pat if is_bad else None, name))
    last_end = end

if last_end < (1<<32)-1:
  ranges.append(('bad', last_end+1, (1<<32)-1, 'gap', '(gap)'))


print('skipping gaps/islands...')

#Need to skip gaps now so that they won't be used to ignore many good islands

for x in range(len(ranges)-2):
  if ranges[x][0] == 'good' and ranges[x+1][3] == 'gap' and ranges[x+2][0] == 'good':
    rl = ranges[x+1][2] - ranges[x+1][1] + 1

    if rl < min_gap_ignore:
      ranges[x+1] = ('good', ranges[x+1][1], ranges[x+1][2], 'gap-skipped', ranges[x+1][4])
      skipped_gaps += rl

    if rl >= print_gaps_min:
      print('gap of size', math.log(rl, 2), rl,  long2ip(ranges[x+1][1])+'-'+long2ip(ranges[x+1][2]))

"""
Now we want to remove small good "islands".
We do it first so that in 50/50 island fill, it's all marked as bad.
"""

for x in range(len(ranges)-2):
  if ranges[x][0] != 'good' and ranges[x+1][0] == 'good' and ranges[x+2][0] != 'good':
    rl = ranges[x+1][2] - ranges[x+1][1] + 1

    if rl <= max_good_ignore:
      ranges[x+1] = ('bad', ranges[x+1][1], ranges[x+1][2], 'skipped', ranges[x+1][4])


print('merging...')

#now merge so we know what to leave and what not

merged_ranges = []
last_good = False

for kind, start, end, what, name in ranges:
  is_good = kind == 'good'

  if is_good != last_good or not merged_ranges:
    merged_ranges.append([kind, start, end, []])
  else:
    merged_ranges[-1][2] = end

  merged_ranges[-1][3].append((end-start+1, what, name))

  last_good = is_good

print('generating ignored ranges...')


#now we can convert merged_ranged to ignored_ranges and compute stats

ignored_ranges = []

for btype, start, end, items in merged_ranges:
  blocksize = end-start+1

  if btype == 'good':
    if print_small and blocksize < print_small:
      print('small block of', blocksize, 'containing', ', '.join([name for _, _, name in items][:print_small_size]), 'near', long2ip(start))

    continue


  if blocksize >= min_ignore:
    ignored_ranges.append((start, end))
    for size, what, name in items:
      if what == 'skipped':
        skipped_good += size

        print('ignoring good block for', name, 'of size', size, '@', long2ip(start))
      elif what == 'gap-skipped':
        #minus because we've counted that as not ignored
        skipped_gaps -= size
      elif what == 'gap':
        gaps_size += size
      else:
        pattern_ignored_sum[what] += size

  else: #too small, so this is not ignored
    for size, what, name in items:
      if what == 'gap':
        skipped_gaps += size
      elif what == 'gap-skipped' or what == 'skipped':
        #gap-skipped was already counted as ignored
        pass
      else:
        skipped_bad += size


for start, end in ignored_ranges:
  ignored_by_us += end - start + 1


#Now we want to merge ranges with those from input files
print('merging with input')


for infile in infiles:
  with open(infile, 'r') as f:
    for r in ranges_from_file(f):
      already_ignored += r[1] - r[0] + 1
      ignored_ranges.append(r)


#main merge algorithm

new_ranges = merge_ranges(ignored_ranges)
total_ignored = ranges_total(new_ranges)

with open(outfile, 'w') as f:
  for line in output_ranges(new_ranges, not force_cidr_output):
    f.write(line+'\n')

# Stats time!

print(total_ignored, 'IP addresses now ignored')
print(already_ignored, 'were in input files')
print('we ignored', ignored_by_us-gaps_size, 'via patterns and', gaps_size, 'via gaps = ', ignored_by_us, 'in total')
print('we skipped', skipped_good, 'good addrs')
print("didn't ignore", skipped_bad, "addrs and", skipped_gaps, "unreachable, total:", skipped_bad+skipped_gaps)
print(len(new_ranges), 'ranges written to file')
print('')

for pat in sorted(ignore_patterns, key=lambda x: pattern_ignored_sum[pattern_map[x]], reverse=True):
  print(pattern_ignored_sum[pattern_map[pat]], 'ignored by "'+str(pat)+'"')

if ignore_pattern_groups:
  print('')

  group_results = []
  for name, patterns in ignore_pattern_groups:
    total = 0

    for pat in patterns:
      total += pattern_ignored_sum[pattern_map[pat]]

    group_results.append((name, total))

  for name, total in sorted(group_results, key=lambda x: x[1], reverse=True):
    print(total, 'ignored by', name, 'group')



if print_matched_names:
  for pat in ignore_patterns:
    print('')
    print('Names matched by "'+str(pat)+'":')
    for name in sorted(pattern_matched_names[pattern_map[pat]]): #itertools.islice(pattern_matched_names[pattern_map[pat]], 10):
      print('  ', name)

