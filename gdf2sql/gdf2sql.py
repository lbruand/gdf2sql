from dataclasses import dataclass
from numbers import Number
from typing import List, Any

import geopandas as gpd
from shapely import Geometry, to_wkb


@dataclass
class VHeader:
    tablename: str
    colnames: List[str]

    def __str__(self):
        list_colnames = ", ".join( [ f"{colname}" for colname in self.colnames])
        return f'{self.tablename}({list_colnames})'


@dataclass
class VValue:
    data: Any

    def __str__(self):
        if isinstance(self.data, str):
            return f"'{self.data}'"
        elif isinstance(self.data, Number):
            return str(self.data)
        elif isinstance(self.data, Geometry):
            return f"'{to_wkb(self.data, hex=True)}'::geometry"
        else:
            assert False, f"{self.data.__class__}"


@dataclass
class VRow:
    values: List[VValue]

    def __str__(self):
        values = ", ".join([str(value) for value in self.values])
        return f"({values})"


@dataclass
class VRows:
    rows: List[VRow]

    def __str__(self):
        rows_str = ",\n".join([str(row) for row in self.rows])
        return f"AS (VALUES {rows_str})"


@dataclass
class VTable:
    header: VHeader
    rows: VRows

    def __str__(self):
        return f"{self.header} {self.rows}"


def build_vtable(tablename: str, gdf: gpd.GeoDataFrame) -> VTable:
    return VTable(header=VHeader(tablename=tablename, colnames=gdf.columns),
                  rows=VRows(rows=[build_vrow(tuple) for tuple in gdf.itertuples()]))


def build_vrow(tuple):
    values = [VValue(v) for k, v in tuple._asdict().items() if k != 'Index']
    return VRow(values=values)