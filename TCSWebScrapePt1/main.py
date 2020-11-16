#Imports needed

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

#Function to open connection to TCS page with specified unit tables:

def metaObtainer(unit):
    url = 'https://tcs.ucop.edu/tcs/jsp/nonAcademicTitlesSearch.htm'
    data = {'titleCode': '', 'titleName': '', 'effectiveDate': '11/16/2020',
            'titleUnitCode': f'{unit}', 'occupationalSubgroupCategory': 'All',
            'campus': 'All', '_perPgmPssCheckBox': 'no', 'perPgmPssCheckBox': 'on',
            '_perPgmSmgCheckBox': 'no', 'perPgmSmgCheckBox': 'on', '_perPgmMspCheckBox': 'no', 'perPgmMspCheckBox': 'on', '_payRepCovCheckBox': 'no', 'payRepCovCheckBox': 'on', '_payRepUncCheckBox': 'no', 'payRepUncCheckBox': 'on', '_salaryStepCheckBox': 'no', 'salaryStepCheckBox': 'on', '_salaryMeritCheckBox': 'no', 'salaryMeritCheckBox': 'on', 'submitNAT': 'Search'}

    #open session and pass url and form data to access title list page
    with requests.Session() as s:
        p = s.post(url, data=data)

        return p.text

#Function to collect headers and table data from passed unit TCS page        

def metaReader(metaObtainer, unit):
    res = metaObtainer(unit)

    #convert returned title list page to soup object then start extracting needed elements
    soup = BeautifulSoup(res, 'html.parser')
    table = soup.find("table", {"class": "tcs"})

    headers_html = table.select("thead tr:nth-of-type(2) th")
    headers = []
    [headers.append(i.text) for i in headers_html]

    body_html = table.select("tbody tr")

    items = []
    for tr in body_html:
        items.append(tr.get_text(separator=",", strip=True))
    
    body = []
    for i in items:
        rows = []
        for j in i.split(','):
            rows.append(j)  
        body.append(rows)

    return headers, body

#Function to clean data for each unit in Pandas

def metaFormatter(unit):
    headers, body = metaReader(metaObtainer, unit)

    df = pd.DataFrame(data=body, columns=headers)

    df.rename(columns={'Business Unit': 'Campus'}, inplace=True)
    df.drop(columns=['Per Pgm', 'OSC'], inplace=True)

    return df

#Call metaFormatter on units of interest and concat into on dataframe saved as CSV

hx = metaFormatter('HX')
tx = metaFormatter('TX')
rx = metaFormatter('RX')

data = pd.concat([hx, rx, tx], ignore_index=True)

data.to_csv('titles.csv', index=False)