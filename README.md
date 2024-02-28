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
result_query = build_test_sql_query(tables, inner_query)

# Run the result query inside postgresql.
# It will run as if there as a nyc_subway_stats table containing the `df` dataframe.
```

## How does it work under the hood : Injection


Let's take a query example :

```SQL
SELECT name
FROM nyc_subway_stats
WHERE nyc_subway_stats.name = 'Brasilia'
```
(A)

Is transformed into :

```SQL
WITH
nyc_subway_stats(name, Country, Population, Latitude, Longitude) AS (VALUES
('Buenos Aires', 'Argentina', 20.0, -34.58, -58.66),
('Brasilia', 'Brazil', 25.0, -15.78, -47.91),
('Santiago', 'Chile', 9.0, -33.45, -70.66),
('Bogota', 'Colombia', 8.0, 4.6, -74.08),
('Caracas', 'Venezuela', 5.0, 10.48, -66.86)),
INNERQUERY_6cee68 as (SELECT name FROM nyc_subway_stats WHERE nyc_subway_stats.name = 'Brasilia') SELECT * FROM INNERQUERY_6cee68
```

With two common table expressions :

 * one for the mock table `nyc_subway_stats` that overrides the actual content of the real `nyc_subway_stats` ( which might not even exist)
 * one for the inner query A

![Diagram](https://kroki.io/excalidraw/svg/eNrtWltz2sgSfvevoDgP-xK0c79s1XmwHWwTHOIYbJxstlwKCBAISZaEMUnlv5-R7ICuIDs48eagVKXM3NTT6v6-7p75ulepVIOFa1T_qlSNu55umX1Pn1dfhe23huebjq26UPTbd2ZeLxo5CgLX_-vPP1cztJ4zvZ9lWMbUsANfjftb_a5Uvkb_qx6zH85tWpMZPbRa4zt0c9rw3H3jdtCMpkaDlsJYlun6xqrjTrVSxJe_F-o3FGT5e272g1Eoq8QaiD9sOWRkmMNREI5Bq0bdHlrhG8GyxQ88Z2IcOpbjhZL8Bxrhv5Ukn_XeZOg5M7u_GjOIntWYgWlZ7WARrawUp5RUTa3f_S5vqr1olnrhcGQbfqhYuGx1XL1nBpEuwGoHoXRuox99g39WMnn61GiEH8GeWVZ8Ybv_sHCiwzeMfqRkCZlgQCw7YoZBQLq15diRkUAgBYBQTV2OMP3XyjqCaNWBbvnGSqWhDPW05cStJ2EcgXEXLDUTs63D7mifNVoj9_bmizvodlrzEyGry3HfXuUvez95ejGd-f7pde-seXHSmx8MnFbvJvmW7-_XPc-Zx9Z9-Gul6pnb1-_3CTmQEEsmAeMro7NMe5JWt-X0JivV7MUETnlQ_i4zHpRQ0r37cK4hiaDgghIphUw4E0JIA0pQjDmiEgGYcS0okYawejgBCBPMada1IAU71yrrWoIgiCFBJMe1IINFrkUx5CTueuUdKyHFj1vpyuhCY1OabddP64ediq3U8ck-On_3tvLJthe9a3_2ea4vrv1AD_xPdvekfl7P6dFUk5pZ-W_ljwNP903L1P-IfXjHDtrml1ADCCRaj_SpaS0SXy8UaN8yh6Eqqz21e8OrxvUZmIq6lgOmZr9vJezQN9TuIxwjeNncU-_SVbPXKENljmcOTVu3OoW6KdJMRi9rtBKKebL0Pg3RNcjxvjen7vHFxbj27vJ8gt9djVsQlOReheQp8uVyR77PTr7K1YUkTOSxLyaokH0FwQAQHAuQfph9H2xo1q03-VXr7AMGHft9G3y0L0k5mnz1NFb_0JFioM-sLjvbnyysm_pbcd0ty-r1Zo0tWvt3k4_Nk-ZR44qy3qC1LVbnhGFGtsPq-bssweoQwQStp1hdde5Y_ef6LBQMc2UcebSOimldeToDELEdsf9qYt_Aky-P2I8umHd0bJ0T5y2etrpKLR_Euyx4eEYvuHffZF6ARQIzajBmK0tqB0iT8YfnwIRAO5goCxMqhJcUS4pyg39ZiBIqIpAYUPQT8-rzTkMcn96CeW3WbhxMuueTsXHz2-XV-bssk1cTpkFEUz4EQZZqBdPy6HXHro9wG0QBVuFObjkKFZajOBNqDsfsBXJroH-2jCxp_mqCLObHDXST5seN-3sM1Zleu92hk8H1UXsAj0_eN0D79Ko01UGCcMpPBf43cF3Pc3y_NtKD3uhf67oICKIWZ9micZjMxgA0U0pGUHUjAbadzP4ANz0xmWXcnU_eTMZ2e2yOm5fvhwy5s5eRzHJI4JaS2fxdlklmCYY5XIqkRkuzaaxtx6YbXJIBDKBEOC8IJYAXeiSVahKkaPupKmeEM_QjdHroTKeOXemErKNy0fqd6ykFKOlfHsXGDsdSFLuB5tIUm9hzuR0_hnS7AZwf3clxaxbU9s_OwJsucMflSRfydIIp4O-bYPadILTol1A8FpJxTHL5FvHiQhSWmMInhcovrHSsv7liLfv8yxv0Eb7uXB7PRcvefxwrUi4w3Q4r5ktThhVDqsvJMOkuw3yOMBUirjwAQ5QbpoLiY1mVZFL5pCOXXYqZ4r8NjPOsKeb6rCCFUQlHZZhrHCtD4JIgFVglaQ_K5OEozN5ewkhDAEjEqIQcEUDzDmOI1KSAnBJJEaYgFkTsfHvj2QwiRJCCFBQWB7ychp8EcPSCnNt1zDTr_h3jQBAnRLD8-59XuaOLLS98sja3Wi9DopbuB2FAaoZx0FkoZOZrBLoXHJh237SHqm_F6d-vD5apM0X41JuFCgBKdgQl4AIQRikBgsdGDXU3imr2UsFE1bD7m4VYf8sjIQRkEEgsCRQCUoEhywpBNUAkAYRywlXuRXhGqEg3-yG2jAw9Y-BK5HhfPFAquPOxNuhaB2aKBteiGfm_RbMXE-ErO1OJkshFM4aL72YKADGmnG-_Gs6x4FDs0CwHSNaHNEkgkRJQRlQIKjhTiJYDZmnnexq4rT_pXgdupAjcEOIICpVBUimfG9ysbqd29nZ4etWtjRZkYHbN18FhKXATsUrCvYvmVCQw1DChmGAAwzwQoSx8kV3sVTr2YlQIxlDuTXKJi8AKYYSFoJz9rpFXsZmFT41sE5vS7rYZIWaDADc_fwH2Zb3p15ozqz45XuQhRA1qHGUw4dkhYL18a4oq8SPkRcSX2WoKZhoSGIfxGlEIQfOus-5OG0ojQHi5UFCWF62INdVIRSdqmkTbrkeuZ4-ffTMlU7PRB4HhVYb9AfJvrG1UaixjEKyp0wSOm39RruiQIrGZdEWmQPrH1GHWH3euTV0oEhqCWDD1IVTmHrukG-kHbUxdIOEagYhJIRX5MAZITurCoSYp45iryIiqPAnvoKAsFGCmtC5p7JBhhQW0-Fo7psqxKJboec4dyS8PBmrFhhdlLhmT-xmZy_rDyHgMADQKmYSQQqy-LiAMba0OUzpVUUJAQpQYHBCVhSDGVxHnUgquqSQ4NELEOeRyq3WYvYePUNVdtx0oM1vuSvmQ2X8A79Vy1VvTmB8U-__eg1ih_xvhDr9-2_v2P7tw3_o=)

<!--[Edit this diagram](https://niolesk.top/#https://kroki.io/excalidraw/svg/eNrtWltz2sgSfvevoDgP-xK0c79s1XmwHWwTHOIYbJxstlwKCBAISZaEMUnlv5-R7ICuIDs48eagVKXM3NTT6v6-7p75ulepVIOFa1T_qlSNu55umX1Pn1dfhe23huebjq26UPTbd2ZeLxo5CgLX_-vPP1cztJ4zvZ9lWMbUsANfjftb_a5Uvkb_qx6zH85tWpMZPbRa4zt0c9rw3H3jdtCMpkaDlsJYlun6xqrjTrVSxJe_F-o3FGT5e272g1Eoq8QaiD9sOWRkmMNREI5Bq0bdHlrhG8GyxQ88Z2IcOpbjhZL8Bxrhv5Ukn_XeZOg5M7u_GjOIntWYgWlZ7WARrawUp5RUTa3f_S5vqr1olnrhcGQbfqhYuGx1XL1nBpEuwGoHoXRuox99g39WMnn61GiEH8GeWVZ8Ybv_sHCiwzeMfqRkCZlgQCw7YoZBQLq15diRkUAgBYBQTV2OMP3XyjqCaNWBbvnGSqWhDPW05cStJ2EcgXEXLDUTs63D7mifNVoj9_bmizvodlrzEyGry3HfXuUvez95ejGd-f7pde-seXHSmx8MnFbvJvmW7-_XPc-Zx9Z9-Gul6pnb1-_3CTmQEEsmAeMro7NMe5JWt-X0JivV7MUETnlQ_i4zHpRQ0r37cK4hiaDgghIphUw4E0JIA0pQjDmiEgGYcS0okYawejgBCBPMada1IAU71yrrWoIgiCFBJMe1IINFrkUx5CTueuUdKyHFj1vpyuhCY1OabddP64ediq3U8ck-On_3tvLJthe9a3_2ea4vrv1AD_xPdvekfl7P6dFUk5pZ-W_ljwNP903L1P-IfXjHDtrml1ADCCRaj_SpaS0SXy8UaN8yh6Eqqz21e8OrxvUZmIq6lgOmZr9vJezQN9TuIxwjeNncU-_SVbPXKENljmcOTVu3OoW6KdJMRi9rtBKKebL0Pg3RNcjxvjen7vHFxbj27vJ8gt9djVsQlOReheQp8uVyR77PTr7K1YUkTOSxLyaokH0FwQAQHAuQfph9H2xo1q03-VXr7AMGHft9G3y0L0k5mnz1NFb_0JFioM-sLjvbnyysm_pbcd0ty-r1Zo0tWvt3k4_Nk-ZR44qy3qC1LVbnhGFGtsPq-bssweoQwQStp1hdde5Y_ef6LBQMc2UcebSOimldeToDELEdsf9qYt_Aky-P2I8umHd0bJ0T5y2etrpKLR_Euyx4eEYvuHffZF6ARQIzajBmK0tqB0iT8YfnwIRAO5goCxMqhJcUS4pyg39ZiBIqIpAYUPQT8-rzTkMcn96CeW3WbhxMuueTsXHz2-XV-bssk1cTpkFEUz4EQZZqBdPy6HXHro9wG0QBVuFObjkKFZajOBNqDsfsBXJroH-2jCxp_mqCLObHDXST5seN-3sM1Zleu92hk8H1UXsAj0_eN0D79Ko01UGCcMpPBf43cF3Pc3y_NtKD3uhf67oICKIWZ9micZjMxgA0U0pGUHUjAbadzP4ANz0xmWXcnU_eTMZ2e2yOm5fvhwy5s5eRzHJI4JaS2fxdlklmCYY5XIqkRkuzaaxtx6YbXJIBDKBEOC8IJYAXeiSVahKkaPupKmeEM_QjdHroTKeOXemErKNy0fqd6ykFKOlfHsXGDsdSFLuB5tIUm9hzuR0_hnS7AZwf3clxaxbU9s_OwJsucMflSRfydIIp4O-bYPadILTol1A8FpJxTHL5FvHiQhSWmMInhcovrHSsv7liLfv8yxv0Eb7uXB7PRcvefxwrUi4w3Q4r5ktThhVDqsvJMOkuw3yOMBUirjwAQ5QbpoLiY1mVZFL5pCOXXYqZ4r8NjPOsKeb6rCCFUQlHZZhrHCtD4JIgFVglaQ_K5OEozN5ewkhDAEjEqIQcEUDzDmOI1KSAnBJJEaYgFkTsfHvj2QwiRJCCFBQWB7ychp8EcPSCnNt1zDTr_h3jQBAnRLD8-59XuaOLLS98sja3Wi9DopbuB2FAaoZx0FkoZOZrBLoXHJh237SHqm_F6d-vD5apM0X41JuFCgBKdgQl4AIQRikBgsdGDXU3imr2UsFE1bD7m4VYf8sjIQRkEEgsCRQCUoEhywpBNUAkAYRywlXuRXhGqEg3-yG2jAw9Y-BK5HhfPFAquPOxNuhaB2aKBteiGfm_RbMXE-ErO1OJkshFM4aL72YKADGmnG-_Gs6x4FDs0CwHSNaHNEkgkRJQRlQIKjhTiJYDZmnnexq4rT_pXgdupAjcEOIICpVBUimfG9ysbqd29nZ4etWtjRZkYHbN18FhKXATsUrCvYvmVCQw1DChmGAAwzwQoSx8kV3sVTr2YlQIxlDuTXKJi8AKYYSFoJz9rpFXsZmFT41sE5vS7rYZIWaDADc_fwH2Zb3p15ozqz45XuQhRA1qHGUw4dkhYL18a4oq8SPkRcSX2WoKZhoSGIfxGlEIQfOus-5OG0ojQHi5UFCWF62INdVIRSdqmkTbrkeuZ4-ffTMlU7PRB4HhVYb9AfJvrG1UaixjEKyp0wSOm39RruiQIrGZdEWmQPrH1GHWH3euTV0oEhqCWDD1IVTmHrukG-kHbUxdIOEagYhJIRX5MAZITurCoSYp45iryIiqPAnvoKAsFGCmtC5p7JBhhQW0-Fo7psqxKJboec4dyS8PBmrFhhdlLhmT-xmZy_rDyHgMADQKmYSQQqy-LiAMba0OUzpVUUJAQpQYHBCVhSDGVxHnUgquqSQ4NELEOeRyq3WYvYePUNVdtx0oM1vuSvmQ2X8A79Vy1VvTmB8U-__eg1ih_xvhDr9-2_v2P7tw3_o=)-->


 ## Benefits

 * No need to update the underlying table before the test (which might be slow).
 * The data and the query are send to be tested inside the postgresql engine directly.
 * gdf2sql is independent of the database considered. So you might decide to unittest in SQLite and then to test integration in postgresQL. ( Beware that SQLite and PostgresQL are different SQL dialect that might affect your queries.)

## Why not use `to_sql` from pandas

https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
To Be Continued
