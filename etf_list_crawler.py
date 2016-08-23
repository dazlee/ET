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

def parseHistory(historyCSV):
    name = ""
    data = []
    reader = csv.reader(historyCSV, delimiter=",")
    header = reader.next()
    data = [row for row in reader]
    return (header, data)

def getETFHistory(ticker):
    history = getHtml("http://chart.finance.yahoo.com/table.csv?a=0&b=1&c=1992&d=7&e=22&f=2016&g=d&ignore=.csv&s=" + ticker)
    # header = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    header, rows = parseHistory(history.split("\n"))
    header_map = {}
    for index, column in enumerate(header):
        if column in ETF_HISTORY_KEYS:
            header_map[index] = ETF_HISTORY_KEYS[column]
    # header_map = {'0' : 'Date', '1': 'open' .....}
    for row in rows:
        for index, data in enumerate(row):
            print header_map[index] + " " + data


if __name__ == '__main__':
    # log = Logger.get_instance()
    # log.info('------------------ ETF WORKER START ------------------')
    # html = getHtml("http://etf.stock-encyclopedia.com/category/us-etfs.html");
    etfs = ['XLE']#extractETFList(html)
    for etf in etfs:
        # html = getHtml("http://etfdb.com/etf/" + etf)
        # should save data into db
        # ETFData = extractETFInfoFromETFDB(html)
        # pprint.pprint(ETFData)
        # get etf history
        ETFHistory = getETFHistory(etf)
