import socket
import struct
import csv
import re
import io
import math
import sys
import itertools

#these are passed to re.compile
ignore_patterns = ('USAISC', 'DoD', r'\bNASA', 'National Aeronautics', '754th', 'Navy Network Information Center', 'DARPA', r'\bUSDA', '^State of ', '(?i)university', '(?i)host', '(?i)research', '(?i)academ(y|ic)', '(?i)institute', '(?i)education')

dbfile = sys.argv[1]
outfile = sys.argv[2]
infiles = sys.argv[3:]

#ranges we print are inclusive

min_ignore = 1 << 14
max_good_ignore = 256
min_gap_ignore = 1 << 17
force_cidr_output = False #set to True for ZMap

## options for debug output from this script

print_matched_names = True
print_gaps_min = 1 << 17

#print max [print_small] items from good blocks smaller than [print_small_size]
print_small = 1024
print_small_size = 4 

####   ####   ####
####   ####   ####
####   ####   ####

def ip2long(ip):
  packedIP = socket.inet_aton(ip)
  return struct.unpack("!L", packedIP)[0]

def long2ip(l):
  return socket.inet_ntoa(struct.pack('!L', l))
  
def ip_range(s):
  if '-' in s:
    a1, a2 = s.split('-')
    try:
      ret = (ip2long(a1), ip2long(a2))
    except:
      print(a1.encode('iso-8859-1'))
      print('w', a2.encode('iso-8859-1'))
      exit()
    return ret
  else:
    if '/' in s:
      addr, pl = s.split('/')
    else:
      addr, pl = s, 32
      
    addr = ip2long(addr)
    nbits = 32-int(pl)
    mask = (1 << nbits) -1
    addr |= mask
   
    return (addr ^ mask, addr)
        
def range_to_cidrs(start, end):
  last_addr = caddr = start
  
  ret = []
  
  while True:
    cplen = 32
    
    while True:
      cplen -= 1
      
      test_bit = 1<<(31-cplen)
      if caddr & test_bit:
        break
        
      new_last = caddr | ((test_bit<<1)-1)
      
      if cplen == -1 or new_last > end:
        break
      else:
        last_addr = new_last  
      
    cplen += 1    

    ret.append((caddr, cplen))
    last_addr = caddr = last_addr+1
    
    if caddr > end:
      break
    
  return ret
  
def cidr_to_str(cidr):
  return long2ip(cidr[0])+'/'+str(cidr[1])

##

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

to_ignore = []
total_ignored = already_ignored = gaps_size = 0
ignored_by_us = skipped_bad = skipped_good = skipped_gaps = 0
pattern_ignored_sum = {}
pattern_matched_names = {}

for pat in ignore_patterns:
  pc = re.compile(pat)
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
    for idx, line in enumerate(f):
      line = line.strip()
      if not line or line[0] == '#':
        continue
    
      r = ip_range(line)
      already_ignored += r[1] - r[0] + 1
      ignored_ranges.append(r)
      
      
#main merge algorithm

ignored_ranges.sort(key=lambda x: x[0])
new_ranges = [list(ignored_ranges[0])]

for r in ignored_ranges:
  if r[0] <= new_ranges[-1][1]+1:
  
    if r[1] > new_ranges[-1][1]:
       new_ranges[-1][1] = r[1]
  else:
    new_ranges.append(list(r))
    

with open(outfile, 'w') as f:
  for start, end in new_ranges:
    total_ignored += end - start + 1
    
    if force_cidr_output:
      for cidr in range_to_cidrs(start, end):
        f.write(cidr_to_str(cidr)+'\n')
    else:
      f.write(long2ip(start)+'-'+long2ip(end)+'\n')
      
# Stats time!

print(total_ignored, 'IP addresses now ignored')
print(already_ignored, 'were in input files')
print('we ignored', ignored_by_us-gaps_size, 'via patterns and', gaps_size, 'via gaps = ', ignored_by_us, 'in total')
print('we skipped', skipped_good, 'good addrs')
print("didn't ignore", skipped_bad, "addrs and", skipped_gaps, "unreachable, total:", skipped_bad+skipped_gaps)
print(len(new_ranges), 'ranges written to file')

for pat in to_ignore:
  print(pattern_ignored_sum[pat], 'ignored by', pat)
  
if print_matched_names:
  for pat in to_ignore:
    print('')
    print('Names matched by '+str(pat)+':')
    for name in pattern_matched_names[pat]: #itertools.islice(pattern_matched_names[pat], 10):
      print('  ', name)
      
      