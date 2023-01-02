from enum import Enum
from debugvisualizer.debugvisualizer import Plotter
from data.plot_data import PlotData
from utils.consts import Consts
from shapely.geometry import Polygon, MultiPolygon

import geopandas
import json
import math
import os



DATA_PATH = "data"
SPLITTED_DATA_PATH = os.path.join(DATA_PATH, "splitted_data")


class Uaa(Enum):
    """plot usage"""
    Plot = 8
    Road = 11


class PlotDataPreprocessor:
    """raw plot data preprocessor"""

    def __init__(self, plots_data: geopandas.GeoDataFrame) -> None:
        self.__plots_data = plots_data.sort_values("PNU").reset_index(drop=True)
        self.__reset_merged_plot()
        self.__gen_preprocessed_data()

    def __reset_merged_plot(self) -> None:
        """merged separated plot polygon"""
        self.__merged_plot = Polygon()

    def __gen_preprocessed_data(self) -> None:
        """main func"""
        self.preprocessed_plots_data = []
        raw_data = self.__plots_data 
        rows, _ = raw_data.shape

        ri = 0
        is_needed_idx_add = False
        while ri < rows - 1:
            if is_needed_idx_add:
                ri += 1

            uaa = raw_data.loc[ri].UAA
            curr_pnu = raw_data.loc[ri].PNU
            next_pnu = raw_data.loc[(ri + 1) % rows].PNU
            prev_pnu = raw_data.loc[(ri - 1) % rows].PNU
            geometry  = raw_data.loc[ri].geometry

            is_needed_idx_add = False
            if int(uaa) != Uaa.Plot.value:
                is_needed_idx_add = True
                continue
            
            if curr_pnu in (prev_pnu, next_pnu):
                self.__merged_plot = self.__merged_plot.union(geometry)
                is_needed_idx_add = True
                continue
            
            self.__merged_plot = geometry if self.__merged_plot.is_empty else self.__merged_plot
            if (
                self.__is_satisfied_area_baseline(self.__merged_plot) 
                or isinstance(self.__merged_plot.simplify(Consts.TOLERANCE), MultiPolygon)
            ):
                self.__reset_merged_plot()
                is_needed_idx_add = True
                continue
            
            self.preprocessed_plots_data.append(
                PlotData(plot_geometry=self.__merged_plot)
            )
            
            self.__reset_merged_plot()
            is_needed_idx_add = True
            
    def __is_satisfied_area_baseline(self, plot: Polygon) -> bool:
        area_baseline_min = 100
        area_baseline_max = 400
        
        return plot.area <= area_baseline_min or plot.area >= area_baseline_max
    
    @staticmethod
    def split_geojson(geojson_dict, batch=5000):
        """geojson splitter"""
        features = geojson_dict["features"]
        split_count = math.ceil(len(features) / batch)

        for b in range(split_count):
            
            splitted_dict = {
            "type": "FeatureCollection",
            "name": f"gangnam-plots-{b}",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::5174" } },
            "features": features[b * batch : (b+1) * batch]
            }
            
            save_path = os.path.join(f"{SPLITTED_DATA_PATH}", splitted_dict["name"] + ".geojson")
            with open(save_path, "w", encoding="UTF-8") as f:
                json.dump(splitted_dict, f)


        
if __name__ == "__main__":
    
    # with open(f"{DATA_PATH}/gangnam-plots-all.geojson", "r", encoding="UTF-8") as f:
    #     PlotDataPreprocessor.split_geojson(json.load(f))
    
    for geojson in os.listdir(SPLITTED_DATA_PATH):
        geojson_path = os.path.join(SPLITTED_DATA_PATH, geojson)
        preprocessed_plots_data = PlotDataPreprocessor(geopandas.read_file(geojson_path))
        pass  # break point
