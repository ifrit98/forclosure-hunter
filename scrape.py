#!/usr/bin/python3

from bs4 import BeautifulSoup
from pprint import pprint
import requests
import os

from sys import argv
import json
import time


#url = "https://www.foreclosurelistings.com/list/NY/ONONDAGA/SYRACUSE/"
#url = "https://public-gslb.epropertyplus.com/landmgmtpub/app/base/landing"
url = "https://www.bankforeclosuressale.com/list/ny/county067/syracuse.html"

# Make a GET request to fetch the raw HTML content
html_content = requests.get(url).text

# Parse the html content
soup = BeautifulSoup(html_content, "lxml")
print(soup.prettify()) # print the parsed data of html

soup_all = soup.find_all("a")
base_url = soup_all[1].get("href") # 'https://www.bankforeclosuressale.com'

props = []
for link in soup_all:
    print("Inner Text: {}".format(link.text))
    print("Title: {}".format(link.get("title")))
    print("href: {}".format(link.get("href")))
    if link.get("href"):
        if link.get("href")[:17] in ['/pre-foreclosure/', '/foreclosure-list']:
            props.append(base_url + link.get("href")[1:])


pprint(props)

props_info = []
for url in props:
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    # print(soup.prettify()) # print the parsed data of html

    # TODO: Parse property data and populate to a csv or json file
    soup_divs = soup.find_all("div")
    dolla_divs = []
    for div in soup_divs:
        start = div.text.find("$")
        if start != -1:
            end = -1 # div.text.find("*")
            print("Found proerty info")
            print("Inner Text: {}".format(div.text[start:end]))
            # print("Title: {}".format(div.get("title")))
            # print("href: {}".format(div.get("href")), "\n")
            dolla_divs.append(div)
            break


    import re
    rm_comma = ",(?!\s+\d$)"
    price_exp = "(?:[\£\$\€]{1}[,\d]+.?\d)"
    
    price = re.findall(price_exp, dolla_divs[0].text[start:end])[0]
    price = float(re.sub(rm_comma, '', price[1:])) # extract out '$' and remove commas `,`
    print(price)

    bed_exp = "(?:Bedrooms: \d)"
    bedrooms = float(re.findall(bed_exp, dolla_divs[0].text[start:end])[0][-1])
    print("BEDROOMS:", bedrooms)

    bath_exp = "(?:Bathrooms: \d)" 
    bathrooms = float(re.findall(bath_exp, dolla_divs[0].text[start:end])[0][-1])
    print("BATHROOMS:", bathrooms)

    lot_sqft_exp = "Lot Square Foot: \d+"
    lot_sqft = re.findall(lot_sqft_exp, dolla_divs[0].text[start:end])[0]
    lot_sqft = int(lot_sqft[17:]) 
    print("LOT SQFT:", lot_sqft)

    sqft_exp = "Building Square Foot: \d+"
    sqft = re.findall(sqft_exp, dolla_divs[0].text[start:end])[0]
    sqft = int(sqft[22:]) 
    print("SQFT:", sqft)

    year_exp = "Age of the Building: \d+"
    year = re.findall(year_exp, dolla_divs[0].text[start:end])[0]
    year = int(year[-4:])
    print("YEAR BUILT:", year)

    dolla_idx = start + len(str(price))
    end_idx = dolla_divs[0].text.find("NY") + 8
    address_str = dolla_divs[0].text[dolla_idx:end_idx]
    address = re.sub('\n', ' ', address_str)
    print("ADDRESS:", address)
    
    # addr_exp = "[A-z]*[A-z]*\d* NY \d\d\d\d\d"
    # re.findall(addr_exp, dolla_divs[0].text[start:end])

    prop = {
        "address": address,
        "price": price,
        "beds": bedrooms,
        "baths": bathrooms,
        "sqft": sqft,
        "lot_sqft": lot_sqft,
        "year": year
    }
    print(prop)

    props_info.append(prop)

    # Download photos to sub directory structure?
    print("---------------------------------------------------------------")



friendly_timestamp = lambda: time.strftime("%m_%d_%y_%H-%M-%S", time.strptime(time.asctime()))


outfile = argv[1] if len(argv) > 1 else "syracuse_foreclosures"

outfile = outfile + "_" + friendly_timestamp() + ".json"
with open(outfile, 'w') as f:
    json.dump(props_info, f)