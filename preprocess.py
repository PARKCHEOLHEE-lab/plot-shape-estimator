import shapely
import geopandas

from debugvisualizer.debugvisualizer import Plotter
from data.data import Plot



class PlotDataPreprocessor:
    """raw plot data preprocessor"""

    def __init__(self, plots_data: geopandas.GeoDataFrame) -> None:
        self.__plots_data = (plots_data.sort_values("PNU").reset_index(drop=True))
        self.__gen_preprocessed_data()

    def __gen_preprocessed_data(self) -> None:
        raw_data = self.__plots_data 
        rows, _ = raw_data.shape

        for idx in range(rows):
            curr_uaa = raw_data.loc[idx].UAA
            curr_pnu = raw_data.loc[idx].PNU
            next_pnu = raw_data.loc[(idx + 1) % rows].PNU

            geometry  = raw_data.loc[idx].geometry

            # Plot()



if __name__ == "__main__":
    PlotDataPreprocessor(geopandas.read_file("data/sample-plots.geojson"))
