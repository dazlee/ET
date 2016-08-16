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

    def commit_etf(self, row):
        conn = self.engine.connect()
        ticker = row.get('ticker')
        stmt = select([etf]).where(etf.c.ticker == ticker)

        if conn.execute(stmt).fetchone():
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            stmt = etf.update().where(etf.c.ticker == ticker).values(\
                name=row.get('name'),\
                issuer=row.get('highest_price'),\
                structure=row.get('structure'),\
                inception=row.get('inception'),\
                track=row.get('track'),\
                category=row.get('inception'),\
                asset_class=row.get('asset_class'),\
                asset_class_size=row.get('asset_class_size'),\
                asset_class_style=row.get('asset_class_style'),\
                sector_general=row.get('sector_general'),\
                sector_specific=row.get('sector_specific'),\
                region_general=row.get('region_general'),\
                region_specific=row.get('region_specific'),\
                asset_allocation=row.get('asset_allocation'),\
                sector_breakdown=row.get('sector_breakdown'),\
                market_cap_breakdown=row.get('market_cap_breakdown'),\
                region_breakdown=row.get('region_breakdown'),\
                market_tier_breakdown=row.get('market_tier_breakdown'),\
                country_breakdown=row.get('country_breakdown'),\
                updated_at=updated_at\
            )

            try:
                conn.execute(stmt)
            except Exception as e:
                logger.error('Failed to update etf: %s, %s', e, etf)
        else:
            row.setdefault('created_at', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            try:
                conn.execute(etf.insert(), [row])
            except Exception as e:
                logger.error('Failed to insert etf: %s, %s', e, etf)

        conn.close()

    def commit_history(self, rows):
        conn = self.engine.connect()
        trans = conn.begin()

        try:
            conn.execute(etf_history.delete())
            conn.execute(etf_history.insert(), rows)
            trans.commit()
        except Exception as e:
            trans.rollback()
            logger.error('Failed to insert etf history: %s', e)
            raise
        
        conn.close()


        
