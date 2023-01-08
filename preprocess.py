from enum import Enum
from debugvisualizer.debugvisualizer import Plotter
from data.plot_data import PlotData
from utils.consts import Consts
from utils.utils import ShapeLabel

from shapely.geometry import Polygon, MultiPolygon
from shapely import wkt

import io
import pandas
import geopandas
import json
import math
import os
import csv
import matplotlib.pyplot as plt
import yaml
from PIL import Image



DATA_PATH = "data"
SPLITTED_DATA_PATH = os.path.join(DATA_PATH, "splitted_data")
PREPROCESSED_DATA_PATH = os.path.join(DATA_PATH, "preprocessed_data")
END_DATA_PATH = os.path.join(DATA_PATH, "end_data")
PREPROCESSED_DATA_MAX_ROW = 1000
SHAPE_LABELS = [shape_label.name for shape_label in ShapeLabel]


class Uaa(Enum):
    """plot usage"""
    Plot = 8
    Road = 11


class PlotDataPreprocessor:
    """raw plot data preprocessor"""

    def __init__(self, plots_data: geopandas.GeoDataFrame) -> None:
        self.__plots_data = plots_data.sort_values("UEC").reset_index(drop=True)
        self.__reset_merged_plot()
        self.__gen_preprocessed_data()

    def __reset_merged_plot(self) -> None:
        """merged separated plot polygon"""
        self.__merged_plot = Polygon()
        
    def __save_data_to_csv(self, plot_data: PlotData) -> None:
        """save object data to csv"""
        
        csv_path = os.path.join(PREPROCESSED_DATA_PATH, SHAPE_LABELS[plot_data.plot_label] + ".csv")
        csv_to_df = pandas.read_csv(csv_path)
        csv_to_df.drop_duplicates(subset=None, inplace=True)
        csv_to_df.to_csv(csv_path, index=False)
        
        row_length, _ = csv_to_df.shape
        if row_length < PREPROCESSED_DATA_MAX_ROW:
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                row = plot_data.all_plot_data
                writer.writerow(row)
            
    def __gen_preprocessed_data(self) -> None:
        """main func"""
        self.preprocessed_plots_data = []
        raw_data = self.__plots_data 
        rows, _ = raw_data.shape

        ri = 0
        is_needed_idx_add = False
        while ri < rows - 1:            
            try:
                if is_needed_idx_add:
                    ri += 1

                uaa = raw_data.loc[ri].UAA
                if uaa is None:
                    is_needed_idx_add = True
                    continue
                
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
                
                plot_data = PlotData(plot_geometry=self.__merged_plot)
                print(ri, "label:", SHAPE_LABELS[plot_data.plot_label])

                self.preprocessed_plots_data.append(plot_data)
                self.__save_data_to_csv(plot_data)
                
                self.__reset_merged_plot()
                is_needed_idx_add = True
            
            except Exception as e:
                self.__reset_merged_plot()
                is_needed_idx_add = True
                print("index:", ri, e)
            
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

    @staticmethod
    def merge_plot_image(preprocessed_data_path: str, path: str = None):
        """save image from preprocessed plot data"""
        shape_label = preprocessed_data_path.split(".")[0].split("\\")[-1]
        save_path = os.path.join(DATA_PATH, "QA", shape_label + ".png") if path is None else path
        if os.path.exists(save_path):
            return

        def fig_to_img(figure):
            """Convert a Matplotlib figure to a PIL Image and return it"""
            buf = io.BytesIO()
            figure.savefig(buf)
            buf.seek(0)
            image = Image.open(buf)

            return image
        
        preprocessed_data_df = pandas.read_csv(preprocessed_data_path)
        preprocessed_data_geometries = preprocessed_data_df.plot_geometry_wkt
        
        dpi = 100
        figsize = (3, 3)
        col_num = 25
        row_num = 40
        img_size = figsize[0] * dpi
        merged_image = Image.new("RGB", (col_num * img_size, row_num * img_size), "white")
        
        current_cols = 0
        output_height = 0
        output_width = 0
        color = "black"
        
        for pi, plot_geometry_wkt in enumerate(preprocessed_data_geometries):
            print(pi)

            figure = plt.figure(figsize=figsize, dpi=dpi)
            
            ax = figure.add_subplot(1, 1, 1)
            ax.axis("equal")
            ax.set_axis_off()
            
            plot_geometry = wkt.loads(plot_geometry_wkt)
            ax.plot(*plot_geometry.boundary.coords.xy, color=color, linewidth=0.6)
            ax.fill(*plot_geometry.boundary.coords.xy, alpha=0.2, color=color)
            plt.gcf().text(
                0.5,
                0.1,
                f"index: {pi}",
                va="center",
                ha="center",
                color="black",
                fontsize=7,
                )
            
            image = fig_to_img(figure)

            merged_image.paste(image, (output_width, output_height))

            current_cols += 1
            if current_cols >= col_num:
                output_width = 0
                output_height += img_size
                current_cols = 0
            else:
                output_width += img_size            
            
            plt.close(figure)

        merged_image.save(save_path)

        
if __name__ == "__main__":
        
    """make csv for saving preprocessed data"""
    # for shape_label in SHAPE_LABELS:
    #     save_path = os.path.join(PREPROCESSED_DATA_PATH, shape_label + ".csv")
    #     if not os.path.exists(save_path):
    #         f = open(save_path, 'w', newline="")
    #         writer = csv.writer(f)
    #         writer.writerow(
    #             [
    #                 "plot_aspect_ratio",
    #                 "plot_obb_ratio",
    #                 "plot_interior_angle_sum",
    #                 "plot_label",
    #                 "plot_geometry_wkt",
    #                 "is_rectangle",
    #                 "is_flag",
    #                 "is_trapezoid",
    #                 "is_triangle"
    #             ]
    #         )
    
    #         f.close()
    
    """preprocessing"""
    # preprocessed_plots_data = PlotDataPreprocessor(geopandas.read_file("data/gangnam-plots-all.geojson"))

    """preprocessed data QA"""
    # for preprocessed_data in os.listdir(PREPROCESSED_DATA_PATH):
    #     preprocessed_data_path = os.path.join(PREPROCESSED_DATA_PATH, preprocessed_data)
    #     PlotDataPreprocessor.merge_plot_image(preprocessed_data_path)
    
    """make end data"""
    
    with open("data/QA/_InvalidShapes.yaml", 'r') as f:
        invalid_shapes_yamal = yaml.safe_load(f)
        for shape_key in invalid_shapes_yamal["invalid_indices"].keys():

            plots_df = pandas.read_csv(os.path.join(PREPROCESSED_DATA_PATH, shape_key + ".csv"))
            plots_df["index"] = range(plots_df.shape[0])

            invalid_indices = sorted(invalid_shapes_yamal["invalid_indices"][shape_key])
            valid_plots_df = plots_df[~plots_df["index"].isin(invalid_indices)]
            
            csv_save_path = os.path.join(END_DATA_PATH, shape_key + ".csv")
            if os.path.exists(csv_save_path):
                continue
            
            valid_plots_df.to_csv(csv_save_path, index=False)
            PlotDataPreprocessor.merge_plot_image(csv_save_path, path=os.path.join(END_DATA_PATH, shape_key + ".png"))
            