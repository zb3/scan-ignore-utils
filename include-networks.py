import re
import io
import sys
import csv
import argparse

from runpy import run_path  
from util import *

                  
print_matched_names = True
force_cidr_output = True #set to True for ZMap

####   ####   ####
####   ####   ####
####   ####   ####

parser = argparse.ArgumentParser()
parser.add_argument('dbfile',  help='CSV file containing IP to ASN mappings')
parser.add_argument('outfile', help='Output file')
parser.add_argument('infile', nargs='*', help='Files with additional ranges to include')
parser.add_argument('-c', default='config.py', help='Config file containing the "include_patterns" array. This defaults to "config.py"')
args = parser.parse_args()


dbfile = args.dbfile
outfile = args.outfile
infiles = args.infile
cfgfile = args.c

cfgdict = run_path(cfgfile)
include_patterns = cfgdict['include_patterns']
include_pattern_groups = cfgdict.get('include_pattern_groups', [])


##

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

to_include = []
already_included = 0
total_included = 0
pattern_included_sum = {}
pattern_matched_names = {}
pattern_map = {}

for pat in include_patterns:
  pc = re.compile(pat)
  pattern_map[pat] = pc
  pattern_included_sum[pc] = 0
  pattern_matched_names[pc] = set()
  to_include.append(pc)
  

print('parsing...')
ranges = []

with open(dbfile, newline='', encoding='utf-8') as csvfile:
  dbreader = csv.reader(csvfile)
  
  next(dbreader)
  
  for block in dbreader:
    block, _, name = block
    
    start, end = ip_range(block)
    is_matched = False
    
    for pat in to_include:
      if pat.search(name):
        if print_matched_names:
          pattern_matched_names[pat].add(name)
          
        is_matched = True
        break
        
    if is_matched:
      ranges.append([start, end])
      pattern_included_sum[pat] += end-start+1



#Now we want to merge ranges with those from input files
print('merging with input...')

for infile in infiles:
  with open(infile, 'r') as f:
    for idx, line in enumerate(f):
      line = line.strip()
      if not line or line[0] == '#':
        continue
    
      r = ip_range(line)
      already_included += r[1] - r[0] + 1
      ranges.append(r)
      
      
#merge
print('merging...')

new_ranges = merge_ranges(ranges)

with open(outfile, 'w') as f:
  for start, end in new_ranges:
    total_included += end - start + 1
    
    if force_cidr_output:
      for cidr in range_to_cidrs(start, end):
        f.write(cidr_to_str(cidr)+'\n')
    else:
      f.write(long2ip(start)+'-'+long2ip(end)+'\n')
      
# Stats time!

print('')
print(total_included, 'IP addresses included')
print(already_included, 'were in input files')
print(len(new_ranges), 'ranges written to file')
print('')

for pat in sorted(include_patterns, key=lambda x: pattern_included_sum[pattern_map[x]], reverse=True):
  print(pattern_included_sum[pattern_map[pat]], 'included by "'+str(pat)+'"')
  
if include_pattern_groups:
  print('')
  
  for name, patterns in include_pattern_groups:
    total = 0
  
    group_results = []
    for pat in patterns:
      total += pattern_included_sum[pattern_map[pat]]
    
    group_results.append((name, total))
  
  for name, total in sorted(group_results, key=lambda x: x[1], reverse=True):
    print(total, 'included by', name, 'group')
  
  
if print_matched_names:
  for pat in include_patterns:
    print('')
    print('Names matched by "'+str(pat)+'":')
    for name in pattern_matched_names[pattern_map[pat]]: #itertools.islice(pattern_matched_names[pat], 10):
      print('  ', name)

