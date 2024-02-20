import unittest
from typing import List

import geopandas as gpd
import pandas as pd

from geoalchemy2 import load_spatialite

from sqlalchemy import create_engine

from sqlalchemy.event import listen

from sqlalchemy import text
import os
from gdf2sql.gdf2sql import build_vtable, VTable, build_test_sql_query


def generate_example_gdf() -> gpd.GeoDataFrame:
    df = pd.DataFrame(
        {
            "name": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
            "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
            "Population": [20., 25., 9., 8., 5.],
            "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
            "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
        }
    )
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
    )
    return gdf


class GDF2SQLTest(unittest.TestCase):
    def test_gdf2sql(self):
        gdf = generate_example_gdf()
        self.assertIsNotNone(gdf)
        table = build_vtable("city_amlat", gdf)
        self.assertIsNotNone(table.rows)
        result = str(table)
        self.assertIsNotNone(result)
        self.assertTrue("VALUES" in result)
        self.assertTrue("'Buenos Aires'" in result)

    def test_inject_queries(self):
        inner_query = "WITH A(v) as (values (0), (1)) SELECT A.v, name, ST_AsText(geom) FROM nyc_subway_stations, A WHERE name = 'Broad St'"
        gdf = generate_example_gdf()
        tables: List[VTable] = [(build_vtable("nyc_subway_stations", gdf))]
        build_test_sql_query(tables, inner_query)

    def test_spacialite(self):
        inner_query = "WITH A(v) as (values (0),print (1)) SELECT A.v, name, ST_AsText(geom) FROM nyc_subway_stations, A WHERE name = 'Broad St'"
        gdf = generate_example_gdf()
        tables: List[VTable] = [(build_vtable("nyc_subway_stations", gdf))]
        query = text(build_test_sql_query(tables, inner_query))
        #query = text('SELECT spatialite_version()')
        print(query)
        os.environ["SPATIALITE_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu/mod_spatialite.so"
        engine = create_engine("sqlite+sqlean://", echo=True)
        listen(engine, "connect", load_spatialite)
        with engine.connect() as db:
            print(db.execute(query).fetchone()[0])


if __name__ == '__main__':
    unittest.main()
