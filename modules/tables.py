from sqlalchemy import Table, Column, Integer, Text, String, Float, MetaData, ForeignKey, DateTime

metadata = MetaData()
etf = Table('etf', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(256)),
    Column('ticker', String(128), unique=True),
    Column('issuer', String(256)),
    Column('structure', String(256)),
    Column('inception', String(256)),
    Column('track', String(256)),
    Column('category', String(256)),
    Column('asset_class', String(256)),
    Column('asset_class_size', String(256)),
    Column('asset_class_style', String(256)),
    Column('sector_general', String(256)),
    Column('sector_specific', String(256)),
    Column('region_general', String(256)),
    Column('region_specific', String(256)),
    Column('asset_allocation', String(256)),
    Column('sector_breakdown', String(256)),
    Column('market_cap_breakdown', String(256)),
    Column('region_breakdown', String(256)),
    Column('market_tier_breakdown', String(256)),
    Column('country_breakdown', String(256)),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
    mysql_charset='utf8',
)
# etf schema:
# id, name, ticker, issuer, structure, inception, track, category,
# asset_class, asset_class_size, asset_class_style,     (optional)
# sector_general, sector_specific,                      (optional)
# region_general, region_specific,                      (optional)
# asset_allocation, sector_breakdown,                   (optional)
# market_cap_breakdown, region_breakdown,               (optional)
# market_tier_breakdown, country_breakdown,             (optional)

# etf history schema:
# id, etf_id, date, open, high, low, close, volume, adj_close
# (all string type)

etf_history = Table('etf_history', metadata,
    Column('id', Integer, primary_key=True),
    Column('ticker', String(128), index=True),
    Column('date', String(256)),
    Column('open', String(256)),
    Column('high', String(256)),
    Column('low', String(256)),
    Column('close', String(256)),
    Column('volume', String(256)),
    Column('adj_close', String(256)),
    mysql_charset='utf8',
)
