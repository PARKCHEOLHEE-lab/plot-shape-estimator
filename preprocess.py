import shapely
import geopandas

from enum import Enum
from debugvisualizer.debugvisualizer import Plotter
from data.data import PlotData
from shapely.geometry import Polygon


class Uaa(Enum):
    """land usage"""
    Plot = 8
    Road = 11


class PlotDataPreprocessor:
    """raw plot data preprocessor"""

    def __init__(self, plots_data: geopandas.GeoDataFrame) -> None:
        self.__plots_data = (plots_data.sort_values("PNU").reset_index(drop=True))
        self.__reset_merged_geometry()
        self.__gen_preprocessed_data()

    def __reset_merged_geometry(self) -> None:
        self.__merged_geometry = Polygon()

    def __gen_preprocessed_data(self) -> None:
        area_baseline = 1000
        plots_data = []
        raw_data = self.__plots_data 
        rows, _ = raw_data.shape

        idx = 0
        while idx < rows:
            uaa = raw_data.loc[idx].UAA
            if int(uaa) != Uaa.Plot.value:
                idx += 1
                continue

            curr_pnu = raw_data.loc[idx].PNU
            next_pnu = raw_data.loc[(idx + 1) % rows].PNU
            prev_pnu = raw_data.loc[(idx - 1) % rows].PNU

            geometry  = raw_data.loc[idx].geometry
            
            if curr_pnu in (prev_pnu, next_pnu):
                self.__merged_geometry = self.__merged_geometry.union(geometry)
                idx += 1
                continue

            if self.__merged_geometry.area >= area_baseline:
                idx += 1
                self.__reset_merged_geometry()

            if self.__merged_geometry.is_empty:
                self.__merged_geometry = geometry
                idx += 1


            plots_data.append(
                PlotData(
                    pnu=curr_pnu, uaa=uaa, geometry=self.__merged_geometry
                )
            )
            self.__reset_merged_geometry()



if __name__ == "__main__":
    PlotDataPreprocessor(geopandas.read_file("data/sample-plots.geojson"))
