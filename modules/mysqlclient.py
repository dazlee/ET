from sqlalchemy import create_engine
from sqlalchemy.sql import select, and_, or_, not_
from tables import *
import time

from modules.logger import Logger

logger = Logger.get_instance()


class MySQLClient(object):
    def __init__(self, user, password, host, dbname):
        conn_str = 'mysql://{0}:{1}@{2}/{3}?charset=utf8'.format(
            user, password, host, dbname)
        self.engine = create_engine(conn_str)

    def create_tables(self):
        metadata.create_all(self.engine)

    def commit_etf(self, etf):
        conn = self.engine.connect()
        ticker = stock.get('ricker')
        stmt = select([etf]).where(etf.c.ticker == ticker)

        if conn.execute(stmt).fetchone():
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            stmt = latest_stock_info.update().where(etf.c.ticker == ticker).values(\
                name=etf.get('name'),\
                issuer=etf.get('highest_price'),\
                structure=etf.get('structure'),\
                inception=etf.get('inception'),\
                track=etf.get('track'),\
                category=etf.get('inception'),\
                asset_class=etf.get('asset_class'),\
                asset_class_size=etf.get('asset_class_size'),\
                asset_class_style=etf.get('asset_class_style'),\
                sector_general=etf.get('sector_general'),\
                sector_specific=etf.get('sector_specific'),\
                region_general=etf.get('region_general'),\
                region_specific=etf.get('region_specific'),\
                asset_allocation=etf.get('asset_allocation'),\
                sector_breakdown=etf.get('sector_breakdown'),\
                market_cap_breakdown=etf.get('market_cap_breakdown'),\
                region_breakdown=etf.get('region_breakdown'),\
                market_tier_breakdown=etf.get('market_tier_breakdown'),\
                country_breakdown=etf.get('country_breakdown'),\
                updated_at=updated_at\
            )

            try:
                conn.execute(stmt)
            except Exception as e:
                logger.error('Failed to update etf: %s, %s', e, etf)
        else:
            etf.setdefault('created_at', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                conn.execute(etf.insert(), [etf])
            except Exception as e:
                logger.error('Failed to insert etf: %s, %s', e, etf)

        conn.close()

    def commit_history(self, rows):
        conn = self.engine.connect()

        conn.close()


        
