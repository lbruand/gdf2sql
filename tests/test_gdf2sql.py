from typing import List

import geopandas as gpd
import pandas as pd
import psycopg2
import sqlglot
from sqlalchemy import create_engine, text

from gdf2sql.gdf2sql import build_vtable, VTable, build_test_sql_query


def generate_example_gdf() -> gpd.GeoDataFrame:
    df = generate_example_df()
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
    )
    return gdf


def generate_example_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
            "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
            "Population": [20., 25., 9., 8., 5.],
            "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
            "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
        }
    )


def test_gdf2sql_gdf():
    gdf = generate_example_gdf()
    assert gdf is not None
    table = build_vtable("city_amlat", gdf)
    assert table.rows is not None
    result = str(table)
    assert result is not None
    assert "VALUES" in result
    assert "'Buenos Aires'" in result
    assert "::geometry" in result


def test_gdf2sql_df():
    df = generate_example_df()
    assert df is not None
    table = build_vtable("city_amlat", df)
    assert table.rows is not None
    result = str(table)
    assert result is not None
    assert "VALUES" in result
    assert "'Buenos Aires'" in result


def test_inject_queries(postgis_server):
    postgis_params = postgis_server['params']

    inner_query = "WITH A(v) as (values (0), (1)) SELECT A.v, name, ST_AsText(geometry)" \
                  " FROM nyc_subway_stats, A " \
                  "WHERE nyc_subway_stats.name = 'Brasilia'"
    gdf = generate_example_gdf()
    tables: List[VTable] = [(build_vtable("nyc_subway_stats", gdf))]
    result_query = build_test_sql_query(tables, inner_query)

    assert result_query is not None

    with psycopg2.connect(**postgis_params) as connection:
        with connection.cursor() as cur:
            cur.execute(result_query)
            res = cur.fetchall()
            assert len(res) == 2
            city, *_ = res
            ix, name, geom = city
            assert name == 'Brasilia'


def test_inject_queries_postgres_to_sqlite():

    inner_query = "WITH A(v) as (values (0), (1)) SELECT A.v, name " \
                  " FROM nyc_subway_stats, A " \
                  "WHERE nyc_subway_stats.name = 'Brasilia'"
    inner_query_as_sqlite = sqlglot.transpile(inner_query, read="postgres", write="sqlite")[0]

    df = generate_example_df()
    tables: List[VTable] = [(build_vtable("nyc_subway_stats", df))]
    result_query = build_test_sql_query(tables, inner_query_as_sqlite)

    assert result_query is not None

    mocked_db = create_engine('sqlite://')
    with mocked_db.connect() as connection:
        result = connection.execute(text(result_query))
        mydata = result.fetchall()
    assert len(mydata) == 2
    city, *_ = mydata
    ix, name = city
    assert name == 'Brasilia'