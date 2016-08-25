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
    results = {}

    heading = soup("div", {"class": "social-share-heading-container"})
    if len(heading) > 0:
        title = heading[0]("h1", {"class": "data-title"})
        if len(title) > 0:
            results['name'] = title[0]("span")[1].text

    uls = soup("ul", {"class": "list-unstyled"})
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
    etf_data['ticker'] = etf
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

    results = []
    for row in rows:
        result = {
            'ticker': ticker
        }
        if len(row) > 0:
            for index, columnKey in headerMap.items():
                result[columnKey] = row[index]
            results.append(result)
    return results


if __name__ == '__main__':
    # log = Logger.get_instance()
    # log.info('------------------ ETF WORKER START ------------------')
    # html = getHtml("http://etf.stock-encyclopedia.com/category/us-etfs.html");
    etfs = ['SPY']#extractETFList(html)
    for etf in etfs:
        etf_data = getETFInfo(etf)
        pprint.pprint(etf_data)
        # ETFData example format:
        # {
        #      'asset_allocation': u'U.S. Stocks::0.9874;;International Stocks::0.0058;;U.S. Bonds::0.0;;International Bonds::0.0;;Preferred Stock::0.0;;Convertibles::0.0;;Cash::0.0068;;Other::0.0',
        #      'asset_class': u'Equity',
        #      'asset_class_size': u'Large-Cap',
        #      'asset_class_style': u'Blend',
        #      'category': u'Large Cap Blend Equities',
        #      'country_breakdown': u'United States::0.9874;;Switzerland::0.0035;;United Kingdom::0.0019;;Singapore::0.0004;;Other::0.0068',
        #      'expense_ratio': u'0.09%',
        #      'inception': u'Jan 22, 1993',
        #      'issuer': u'State Street SPDR',
        #      'market_cap_breakdown': u'Giant::0.4952;;Large::0.3523;;Medium::0.1302;;Small::0.0016;;Micro::0.0',
        #      'market_tier_breakdown': u'Developed::0.9932;;Emerging::0.0',
        #      'name': u'SPDR S&P 500 ETF',
        #      'region_breakdown': u'U.S.::0.9874;;Europe::0.0019;;Asia (Developed)::0.0004;;Middle East::0.0;;Japan::0.0;;Africa::0.0;;Australia::0.0;;Latin America::0.0;;Canada::0.0;;Asia (Emerging)::0.0',
        #      'region_general': u'North America',
        #      'region_specific': u'U.S.',
        #      'sector_general': u'Energy',
        #      'sector_specific': u'Broad',
        #      'sector_breakdown': u'Technology::0.1754;;Health Care::0.1521;;Financial Services::0.1345;;Consumer Cyclical::0.1094;;Industrials::0.1091;;Consumer Defensive::0.1065;;Energy::0.0722;;Communication Services::0.0448;;Utilities::0.0361;;Basic Materials::0.0269;;Real Estate::0.0263',
        #      'structure': u'UIT',
        #      'ticker': 'SPY',
        #      'track': u'S&P 500 Index'
        # }
        # TODO should save to etf db

        # get etf history
        results = getETFHistory(etf)
        # results = [
        #     {
        #          'volume': '1003200',
        #          'ticker': 'SPY',
        #          'adj_close': '28.308155',
        #          'high': '43.9687',
        #          'low': '43.75',
        #          'date': '1993-01-29',
        #          'close': '43.9375',
        #          'open': '43.9687'
        #      },....
        # ]
        # TODO saving history into db
