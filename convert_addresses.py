#!python3

import csv
import re
import argparse
import sys

#                               cruft       name    whatever
revAddressSplitter = re.compile(r"^[^A-Z]*([A-Z \-]+)( .+)?$")
stateAbs = {
    "AUSTRALIAN CAPITAL TERRITORY": "ACT",
    "NEW SOUTH WALES": "NSW",
    "NORTHERN TERRITORY": "NT",
    "QUEENSLAND": "QLD",
    "SOUTH AUSTRALIA": "SA",
    "TASMANIA": "TAS",
    "VICTORIA": "VIC",
    "WESTERN AUSTRALIA": "WA",
}
streetTypes = {
    "ROAD": "RD",
    "STREET": "ST",
    "AVENUE": "AVE",
    "COURT": "CT",
    "CIRCUIT": "CRCT",
    "CCT": "CRCT",
    "PLACE": "PL",
    "DRIVE": "DR",
    "PARADE": "PDE",
    "CLOSE": "CL",
    "ESPLANADE": "ESP",
    "BOULEVARD": "BLVD",
    "SQUARE": "SQ",
    "TERRACE": "TCE",
    "CRESCENT": "CRES",
    "GROVE": "GR",
    "HIGHWAY": "HWY",
    "LANE": "LANE",
    "GARDENS": "GDNS",
    "WAY": "WAY",
    "LOOP": "LOOP",
    "MEWS": "MEWS",
}
stateShorts = set(stateAbs.values())
streetShorts = set(streetTypes.values())


def convert_address(state, origAddress):
    """Normalises states to abbreviation, and
    extracts normalised street names from addresses.
    May raise IndexError, AttributeError, TypeError, KeyError"""

    street = ""
    streetName = ""
    streetType = ""

    rev = (origAddress[::-1]).upper()
    rev = re.sub(r"[,']", "", rev)

    matchme = revAddressSplitter.match(rev)
    street = (((matchme.group(1))[::-1]).strip()).split(" ")

    streetName = " ".join(street[:-1])
    streetType = street[-1]

    state = convert_state(state)

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
    return (state, streetName + " " + streetType)


def convert_state(state):
    """Normalises states to abbreviation"""
    if len(state) > 3 or not state in stateShorts:
        state = stateAbs[state.upper().strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Try and fix street names in addresses for aec_checker.py"
    )
    parser.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin
    )
    parser.add_argument(
        "outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    args = parser.parse_args()

    rdr = csv.DictReader(args.infile)
    wtr = csv.writer(args.outfile, rdr.fieldnames + ["origAddress"])
    wtr.writerow(rdr.fieldnames + ["origAddress"])

    stderr_yet = False

    for row in rdr:
        og = row["streetName"]
        try:
            (state, streetName) = convert_address(row["state"], row["streetName"])
            wtr.writerow(
                [
                    row["givenNames"],
                    row["surname"],
                    row["postcode"],
                    row["suburb"],
                    state,
                    streetName,
                    og,
                ]
            )

        except (IndexError, AttributeError, TypeError, KeyError) as e:
            if not stderr_yet:
                print(
                    "\nThe following entries are anomalous and will need to be manually considered:\n",
                    e,
                    file=sys.stderr,
                )
                print(*(rdr.fieldnames), sep="\t", file=sys.stderr)
                stderr_yet = True
            rv = list(row.values())[:-1]
            print(*rv, file=sys.stderr, sep="\t")
            continue


if __name__ == "__main__":
    main()
