# gdf2sql

## Goal

Simplify testing of PostgresQL SQL queries

The idea is to inject SQL code around the tested query to add mock tables over the actual tables.
The good point is you don't need to modify the tables themselves.
Under the hood, it uses *Common Table Expressions* using the keywords `WITH` to overload
the table with fake data.

As input, it accepts either geopandas dataframes or pandas dataframes.

## Installation

```
pip install git+https://github.com/lbruand/gdf2sql#egg=gdf2sql
```

## Requirements

 * python 3.5+
 * pandas
 * geopandas

## Code example

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
```

## How does it work under the hood : Injection


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



 ## Benefits

 * No need to update the underlying table before the test (which might be slow).
 * The data and the query are send to be tested inside the postgresql engine directly.
 * gdf2sql is independent of the database considered. So you might decide to unittest in SQLite and then to test integration in postgresQL. ( Beware that SQLite and PostgresQL are different SQL dialect that might affect your queries.)