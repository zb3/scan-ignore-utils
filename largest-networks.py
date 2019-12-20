import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('dbfile',  help='CSV file containing IP to ASN mappings')
parser.add_argument('count', type=int, help='how much networks to show (default is %(default)d)', default=100)
parser.add_argument('-a', '--asn', action='store_true', help='shown ASNs')
config = parser.parse_args()

networks = {}
asn_map = {}

with open(config.dbfile, newline='', encoding='utf-8') as csvfile:
  dbreader = csv.reader(csvfile)

  next(dbreader)

  for block in dbreader:
    block, asn, name = block
    
    if name not in networks:
      networks[name] = 0
      if config.asn:
        asn_map[name] = set()
      
    networks[name] += 1 << (32-int(block[block.index('/')+1:]))
    if config.asn:
      asn_map[name].add(asn)

for name in sorted(networks.keys(), key=lambda x: networks[x], reverse=True)[:config.count]:
  if config.asn:
    print(networks[name], name, ','.join(asn_map[name]))
  else:
    print(networks[name], name)