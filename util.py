import socket
import struct

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

def ranges_from_file(f):
  ranges = []

  for line in f:
    line = line.strip()

    if not line or line[0] == '#':
      continue

    r = ip_range(line)
    ranges.append(r)

  return ranges

def merge_ranges(ranges):
  if not ranges:
    return []

  ranges.sort(key=lambda x: x[0])
  new_ranges = [list(ranges[0])]

  for r in ranges:
    if r[0] <= new_ranges[-1][1]+1:

      if r[1] > new_ranges[-1][1]:
         new_ranges[-1][1] = r[1]
    else:
      new_ranges.append(list(r))

  return new_ranges

def invert_ranges(ranges):
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

  return new_ranges

def ranges_total(ranges):
  total = 0

  for start, end in ranges:
    total += end - start + 1

  return total

def output_ranges(ranges, no_cidr=False):
  for start, end in ranges:
    if no_cidr:
      yield long2ip(start)+'-'+long2ip(end)
    else:
      for cidr in range_to_cidrs(start, end):
        yield cidr_to_str(cidr)

