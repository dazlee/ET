# pip install MySQL-python sqlalchemy
import sys
import time
import re
import pprint
import csv

from bs4 import BeautifulSoup
from modules.html import getHtml
from modules.my_math import p2f
from modules.logger import Logger

CONF_FILE_PATH = 'config/stock.conf'
PATTERN = '(\([a-zA-Z0-9-.]+\))';

ETF_INFO_KEYS = {
    "Issuer:": "issuer",
    "Structure:": "structure",
    "Inception:": "inception",
    "Expense Ratio:": "expense_ratio",
    "Tracks This Index:": "track",
    "ETFdb Category:": "category",
    "Asset Class:": "asset_class",
    "Asset Class Size:": "asset_class_size",
    "Asset Class Style:": "asset_class_style",
    "Sector (General):": "sector_general",
    "Sector (Specific):": "sector_specific",
    "Region (General):": "region_general",
    "Region (Specific):": "region_specific",
    "Asset Allocation": "asset_allocation",
    "Sector Breakdown": "sector_breakdown",
    "Market Cap Breakdown": "market_cap_breakdown",
    "Region Breakdown": "region_breakdown",
    "Market Tier Breakdown": "market_tier_breakdown",
    "Country Breakdown": "country_breakdown"
}

ETF_HISTORY_KEYS = {
    'Date': 'date',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume',
    'Adj Close': 'adj_close'
}

def extractETFList(html):
    # extract ETF code list
    result = []
    soup = BeautifulSoup(html)
    tables = soup("table")
    etfAnchors = tables[1]("a")
    for etfAnchor in etfAnchors:
        matches = re.findall(PATTERN, etfAnchor.text)
        count = len(matches)
        if count > 0:
            result.append(matches[count-1][1:-1])
    return result

def extractETFMetaData(html):
    soup = BeautifulSoup(html)
    uls = soup("ul", {"class": "list-unstyled"})
    results = {}
    for ul in uls:
        lis = ul("li")
        for li in lis:
            spans = li("span")
            count = len(spans)
            if count > 0 and spans[0].text in ETF_INFO_KEYS:
                anchor = spans[1]("a")
                key = ETF_INFO_KEYS[spans[0].text]
                value = ""
                if len(anchor) > 0:
                    value = anchor[0].text
                else:
                    value = spans[1].text
                results[key] = value
    return results
def extractETFCombinations(html):
    soup = BeautifulSoup(html)
    results = {}
    chartTables = soup("table", {"class": "chart base-table"})
    for chartTable in chartTables:
        title = chartTable.find_previous_sibling("h3")
        if title.text in ETF_INFO_KEYS:
            key = ETF_INFO_KEYS[title.text]
            value = ""
            tbody = chartTable("tbody")
            if len(tbody) > 0:
                trs = tbody[0]("tr")
                for tr in trs:
                    tds = tr("td")
                    if len(tds) > 1:
                        value += tds[0].text + "::" + str(p2f(tds[1].text)) + ";;"
            results[key] = value[0:-2]
    return results

def extractETFInfoFromETFDB(html):
    soup = BeautifulSoup(html)
    metadata = extractETFMetaData(html)
    combinations = extractETFCombinations(html)
    metadata.update(combinations)
    return metadata

def getETFInfo(etf):
    html = getHtml("http://etfdb.com/etf/" + etf)
    etf_data = extractETFInfoFromETFDB(html)
    return etf_data

def parseHistory(historyCSV):
    data = []
    reader = csv.reader(historyCSV, delimiter=",")
    header = reader.next()
    data = [row for row in reader]
    return (header, data)

def getETFHistory(ticker):
    history = getHtml("http://chart.finance.yahoo.com/table.csv?a=0&b=1&c=1992&d=7&e=22&f=2016&g=d&ignore=.csv&s=" + ticker)
    header, rows = parseHistory(history.split("\n"))
    headerMap = {}
    for index, column in enumerate(header):
        if column in ETF_HISTORY_KEYS:
            headerMap[index] = ETF_HISTORY_KEYS[column]
    return (headerMap, rows)


if __name__ == '__main__':
    # log = Logger.get_instance()
    # log.info('------------------ ETF WORKER START ------------------')
    # html = getHtml("http://etf.stock-encyclopedia.com/category/us-etfs.html");
    etfs = ['SPY']#extractETFList(html)
    for etf in etfs:
        etf_data = getETFInfo(etf)
        # ETFData format:
        # {
        #      'asset_allocation': u'U.S. Stocks::0.989;;International Stocks::0.0031;;U.S. Bonds::0.0;;International Bonds::0.0;;Preferred Stock::0.0;;Convertibles::0.0;;Cash::0.0079;;Other::0.0',
        #      'asset_class': u'Equity',
        #      'category': u'Energy Equities',
        #      'country_breakdown': u'United States::0.989;;Switzerland::0.0031;;Other::0.0079',
        #      'expense_ratio': u'0.15%',
        #      'inception': u'Dec 16, 1998',
        #      'issuer': u'State Street SPDR',
        #      'market_cap_breakdown': u'Giant::0.4268;;Large::0.3903;;Medium::0.1705;;Small::0.0044;;Micro::0.0',
        #      'market_tier_breakdown': u'Developed::0.9921;;Emerging::0.0',
        #      'region_breakdown': u'U.S.::0.989;;Middle East::0.0;;Australia::0.0;;Japan::0.0;;Asia (Developed)::0.0;;Africa::0.0;;Europe::0.0;;Latin America::0.0;;Canada::0.0;;Asia (Emerging)::0.0',
        #      'region_general': u'North America',
        #      'region_specific': u'U.S.',
        #      'sector_breakdown': u'Energy::0.9921;;Financial Services::0.0;;Communication Services::0.0;;Consumer Defensive::0.0;;Real Estate::0.0;;Industrials::0.0;;Consumer Cyclical::0.0;;Basic Materials::0.0;;Technology::0.0;;Health Care::0.0;;Utilities::0.0',
        #      'sector_general': u'Energy',
        #      'sector_specific': u'Broad',
        #      'structure': u'ETF',
        #      'track': u'Energy Select Sector Index'
        # }
        # TODO should save to etf db

        # get etf history
        headerMap, rows = getETFHistory(etf)
        # headerMap = {
        #      0: 'date',
        #      1: 'open',
        #      2: 'high',
        #      3: 'low',
        #      4: 'close',
        #      5: 'volume',
        #      6: 'adj_close'
        # }
        # rows = [['1998-12-22', '23.3125', '23.390619', '23.1875', '23.265619', '15200', '17.099304'], ....]
        # you can uncomment to see data structure
        # ---------------
        # for row in rows:
        #     for index, data in enumerate(row):
        #         print headerMap[index] + " " + data
        # ---------------
        # TODO saving history into db
