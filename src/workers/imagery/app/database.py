import os
from typing import List, Any

import sqlalchemy
from sqlalchemy import create_engine

DATABASE_URL = os.environ["DATABASE_URL"]


class PostgreDB:
    def __init__(self):
        self.metadata = sqlalchemy.MetaData()
        self.Products = sqlalchemy.Table(
            "products",
            self.metadata,
            sqlalchemy.Column("image_id", sqlalchemy.String),
            sqlalchemy.Column("gender", sqlalchemy.String),
            sqlalchemy.Column("master_category", sqlalchemy.String),
            sqlalchemy.Column("sub_category", sqlalchemy.String),
            sqlalchemy.Column("article_type", sqlalchemy.String),
            sqlalchemy.Column("base_colour", sqlalchemy.String),
            sqlalchemy.Column("season", sqlalchemy.String),
            sqlalchemy.Column("year", sqlalchemy.Integer),
            sqlalchemy.Column("usage", sqlalchemy.String),
            sqlalchemy.Column("display_name", sqlalchemy.String),
        )
        self.engine = create_engine(DATABASE_URL)
        self.conn = self.engine.connect()

    def filter_products(self, query: str) -> List[Any]:
        """
        Runs sql query to filter products.

        :param query: query to be executed
        :returns: list of dict containing filtered data
        """
        return [dict(zip(row.keys(), row)) for row in self.conn.execute(query)]
