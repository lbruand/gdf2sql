import unittest
import geopandas as gpd
import pandas as pd


def build_vtable(tablename: str, gdf: gpd.GeoDataFrame) -> str:
    
class GDF2SQLTest(unittest.TestCase):
    def test_gdf2sql(self):
        df = pd.DataFrame(
            {
                "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
                "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
                "Population": [20., 25., 9., 8., 5.],
                "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
                "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
            }
        )
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
        )
        self.assertIsNotNone(gdf)



if __name__ == '__main__':
    unittest.main()
