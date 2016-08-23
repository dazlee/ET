from sqlalchemy import Table, Column, Integer, Text, String, Float, MetaData, ForeignKey, DateTime

metadata = MetaData()
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
