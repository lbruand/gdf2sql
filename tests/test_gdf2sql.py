import unittest
from typing import List

import geopandas as gpd
import pandas as pd

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


def test_gdf2sql():
    gdf = generate_example_gdf()
    assert gdf is not None
    table = build_vtable("city_amlat", gdf)
    assert table.rows is not None
    result = str(table)
    assert result is not None
    assert "VALUES" in result
    assert "'Buenos Aires'" in result

def test_inject_queries():
    inner_query = "WITH A(v) as (values (0), (1)) SELECT A.v, name, ST_AsText(geom) FROM nyc_subway_stations, A WHERE name = 'Broad St'"
    gdf = generate_example_gdf()
    tables: List[VTable] = [(build_vtable("nyc_subway_stations", gdf))]
    result_query = build_test_sql_query(tables, inner_query)
    assert result_query is not None
