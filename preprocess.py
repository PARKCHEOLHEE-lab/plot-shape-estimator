from enum import Enum
from debugvisualizer.debugvisualizer import Plotter
from data.plot_data import PlotData
from shapely.geometry import Polygon

import geopandas



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
            if self.__is_satisfied_area_baseline(self.__merged_plot):
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
        


if __name__ == "__main__":
    preprocessed_plots_data = PlotDataPreprocessor(geopandas.read_file("data/sample-plots.geojson"))
    pd = preprocessed_plots_data.preprocessed_plots_data
    pass  # break point
