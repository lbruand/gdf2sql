# gdf2sql

![GDF2SQL tests](https://github.com/lbruand/gdf2sql/actions/workflows/python-package.yml/badge.svg)

## Goal

Simplify testing of PostgresQL SQL queries

The idea is to inject mock tables as SQL code around the tested query to add mock tables overloading the actual tables.
The good point is you don't need to modify the tables themselves.
Under the hood, it uses *Common Table Expressions* using the keywords `WITH` to overload
the table name with fake data ( but the actual table stays unchanged ).

As input, it accepts either geopandas dataframes or pandas dataframes.

## Installation

```
pip install git+https://github.com/lbruand/gdf2sql#egg=gdf2sql
```

## Requirements

 * python 3.5+
 * pandas
 * geopandas

## Code example Postgis

```python
df = pd.DataFrame(
        {
            "name": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
            "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
            "Population": [20., 25., 9., 8., 5.],
            "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
            "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
        }
    )
inner_query = "SELECT name, ST_AsText(geometry) " \
                  "FROM nyc_subway_stats " \
                  "WHERE nyc_subway_stats.name = 'Brasilia'"
tables: List[VTable] = [(build_vtable("nyc_subway_stats", df))]
result_query = build_test_sql_query(tables, inner_query)

# Run the result query inside postgresql.
# It will run as if there as a nyc_subway_stats table containing the `df` dataframe.
```

## How does it work under the hood : Injection - Postgis


Let's take a query example :

```SQL
SELECT name, ST_AsText(geometry)
FROM nyc_subway_stats
WHERE nyc_subway_stats.name = 'Brasilia'
```
(A)

Is transformed into :

```SQL
WITH
nyc_subway_stats(name, Country, Population, Latitude, Longitude, geometry) AS (VALUES
('Buenos Aires', 'Argentina', 20.0, -34.58, -58.66),
('Brasilia', 'Brazil', 25.0, -15.78, -47.91),
('Santiago', 'Chile', 9.0, -33.45, -70.66),
('Bogota', 'Colombia', 8.0, 4.6, -74.08),
('Caracas', 'Venezuela', 5.0, 10.48, -66.86)),
INNERQUERY_6cee68 as (SELECT name, ST_AsText(geometry) FROM nyc_subway_stats WHERE nyc_subway_stats.name = 'Brasilia') SELECT * FROM INNERQUERY_6cee68
```

With two common table expressions :

 * one for the mock table `nyc_subway_stats` that overrides the actual content of the real `nyc_subway_stats` ( which might not even exist)
 * one for the inner query A


## Code example Postgres

![Diagram](https://kroki.io/plantuml/svg/eNqtVFtPwjAUfu-vOPLilkCzDQnTCNEgCTHGGxrj01LpEZeMFtcZYoz_3bZjsM0pPriXXs75zvedS3eiMpZmb4uE7MOu7-Z-fPsI1xenlztdgex3_vPT6iZMvcC5jAWAM5MqGwQ9ehhS2g1pz4NUrtQg8DxYxTx70bvQtRlZ1EgKfgQOUo5Lne0CRRbFHAbAqzc5pDMEmOIrTGdMgBSAi2Ui3xEVYEHtUc-j1A_0Umf2uwfbMJZ9jfH71Dcgs-Sgvl-AwsAt1b8uYKtRAa9J-DGa07PXLiF7HJ9jgXC1xJRlsRSOYAt0YZYwpcDs4fgYnKu2TJmYa8NwuMEYCc3u0_Y8RRQVb5NuLObNgEn7HZNEriyCbMUYUGT66sIHgXXLorxlrZ0ta1nISFdEe5cnIjfc6hIYg7c-P5gC2YuwRT4JsfnpWkdmE42LThdSTpOYGTzm6Dv2lKA5Fn4V9tJQ_E6uR6SB_Gzb5To9r9KX5qFJgBmJioC-XxMQBpa_aJcteAP9OuzfA34vJHS4XAk90Jsuw5F9xIrUWRtdN883NrNCmopVxZUNORwVIScouPnHfQGCe1rH)

<!--[Edit this diagram](https://niolesk.top/#https://kroki.io/plantuml/svg/eNqtVFtPwjAUfu-vOPLilkCzDQnTCNEgCTHGGxrj01LpEZeMFtcZYoz_3bZjsM0pPriXXs75zvedS3eiMpZmb4uE7MOu7-Z-fPsI1xenlztdgex3_vPT6iZMvcC5jAWAM5MqGwQ9ehhS2g1pz4NUrtQg8DxYxTx70bvQtRlZ1EgKfgQOUo5Lne0CRRbFHAbAqzc5pDMEmOIrTGdMgBSAi2Ui3xEVYEHtUc-j1A_0Umf2uwfbMJZ9jfH71Dcgs-Sgvl-AwsAt1b8uYKtRAa9J-DGa07PXLiF7HJ9jgXC1xJRlsRSOYAt0YZYwpcDs4fgYnKu2TJmYa8NwuMEYCc3u0_Y8RRQVb5NuLObNgEn7HZNEriyCbMUYUGT66sIHgXXLorxlrZ0ta1nISFdEe5cnIjfc6hIYg7c-P5gC2YuwRT4JsfnpWkdmE42LThdSTpOYGTzm6Dv2lKA5Fn4V9tJQ_E6uR6SB_Gzb5To9r9KX5qFJgBmJioC-XxMQBpa_aJcteAP9OuzfA34vJHS4XAk90Jsuw5F9xIrUWRtdN883NrNCmopVxZUNORwVIScouPnHfQGCe1rH)-->



 ## Benefits

 * No need to update the underlying table before the test (which might be slow).
 * The data and the query are send to be tested inside the postgresql engine directly.
 * gdf2sql is independent of the database considered. So you might decide to unittest in SQLite and then to test integration in postgresQL. ( Beware that SQLite and PostgresQL are different SQL dialect that might affect your queries.)

## Why not use `to_sql` from pandas

https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
To Be Continued
