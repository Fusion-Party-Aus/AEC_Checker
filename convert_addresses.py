#!python3

import csv
import re
import argparse
import sys

parser = argparse.ArgumentParser(description="Try and fix street names in addresses for aec_checker.py")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
args = parser.parse_args()

#                               cruft       name    whatever
revAddressSplitter = re.compile(r'^[^A-Z]*([A-Z \-]+)( .+)?$')

stateAbs = {'AUSTRALIAN CAPITAL TERRITORY': 'ACT', 'NEW SOUTH WALES': 'NSW', 'NORTHERN TERRITORY': 'NT', 'QUEENSLAND': 'QLD', 'SOUTH AUSTRALIA': 'SA', 'TASMANIA': 'TAS', 'VICTORIA': 'VIC', 'WESTERN AUSTRALIA': 'WA'}

streetTypes = {'ROAD': 'RD', 'STREET': 'ST', 'AVENUE': 'AVE', 'COURT': 'CT', 'CIRCUIT': 'CCT', 'PLACE': 'PL', 'DRIVE': 'DR', 'PARADE': 'PDE', 'CLOSE': 'CL', 'ESPLANADE': 'ESP', 'BOULEVARD': 'BLVD', 'SQUARE': 'SQ', 'TERRACE': 'TCE', 'CRESCENT': 'CR', 'CRES': 'CR', 'GROVE': 'GR', 'HIGHWAY': 'HWY', 'LANE': 'LANE', 'GARDENS': 'GDNS', 'WAY': 'WAY', 'LOOP':'LOOP', 'MEWS':'MEWS'}

stateShorts = set(stateAbs.values())
streetShorts = set(streetTypes.values())

rdr = csv.DictReader(args.infile)
wtr = csv.DictWriter(args.outfile, rdr.fieldnames + ['origAddress'])
wtr.writeheader()

stderr_yet = False

for row in rdr:
    
    state = row['state']
    address = row['streetName'] # just go with it
    row['origAddress'] = address
    street = ''
    streetName = ''
    streetType = ''

    try:
        rev = (address[::-1]).upper()
        rev = re.sub(r"[,']", '', rev)
        
        matchme = revAddressSplitter.match(rev)            
        street = (((matchme.group(1))[::-1]).strip()).split(' ')
        
        streetName = ' '.join(street[:-1])
        streetType = street[-1]
    
        if len(state) > 3 or not state in stateShorts:
            state = stateAbs[state.upper().strip()]
        
        try:
            if not streetType in streetShorts:
                streetType = streetTypes[streetType]
        except Exception as e:
                for k, v in streetTypes.items():
                    if streetType.startswith(v) or k.startswith(streetType):
                        streetType = v
                        break
                else:
                    raise KeyError
    
        row['state'] = state
        row['streetName'] = streetName + ' ' + streetType
        wtr.writerow(row)
            
    except (IndexError, AttributeError, TypeError, KeyError) as e:
        if not stderr_yet:
            print("\nThe following entries are anomalous and not included:\n", file=sys.stderr)
            print(*(rdr.fieldnames), sep='\t', file=sys.stderr)
            stderr_yet = True
        rv = list(row.values())[:-1]
        print(*rv, file=sys.stderr, sep='\t')
        continue
            