# gdf2sql

## Goal

Simplify testing of PostgresQL SQL queries

The idea is to inject SQL code around the tested query to add fake tables.
Under the hood, it uses *Common Table Expressions* using the keywords `WITH`).
