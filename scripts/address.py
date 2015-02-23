#! /usr/bin/env python3

import os
import sys
import json

def get_addresses(file):
    with open(file) as f:
        lines = f.readlines()
    return lines

def get_points(lat_lng):
    lat, lng = lat_lng.split()
    return [float(lat), float(lng)]

def split_numbers_street_and_lat_lng(line):
    numbers = line.split(']')[0].replace('[','')
    numbers = numbers.split(',')
    street_and_lat_lng = line.split(']')[1].strip()
    street, lat_lng = street_and_lat_lng.split(',')
    return numbers, street, lat_lng

def generate_json(lines):
    addresses = []
    for line in lines:
        if not line.startswith('['):
            address, lat_lng = line.split(',')
            points = get_points(lat_lng.strip())
            address_dict = {"address": address, "lat_lng": points}
            addresses.append(address_dict)
        else:
            numbers, street, lat_lng = split_numbers_street_and_lat_lng(line)
            for number in numbers:
                full_address = "%s %s" % (number, street)
                points = get_points(lat_lng)
                address_dict = {"address": full_address, "lat_lng": points}
                addresses.append(address_dict)

    address_json = json.dumps({"addresses": addresses})
    return address_json


if __name__=='__main__':
    if not len(sys.argv) > 1:
        print('give me a file name!')
        sys.exit(1)

    lines = get_addresses(sys.argv[1])
    address_json = generate_json(lines)
    with open('../import-data/addresses.json', 'w') as f:
        f.write(address_json)


