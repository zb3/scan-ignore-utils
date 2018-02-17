import sys

dct = {}

with open(sys.argv[1], 'r') as f:
  for line in f:
    if line.count('.') < 2:
      continue
      
    line = line.strip()
    
    k = line[:line.index('.', line.index('.')+1)]
    dct[k] = dct.get(k, 0)+1
    
for x in sorted(dct, key=lambda x:dct[x], reverse=True):
  print(x, dct[x])
