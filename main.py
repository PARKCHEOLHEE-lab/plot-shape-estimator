from utils.utils import get_data_and_label
from debugvisualizer.debugvisualizer import Plotter
from shapely import wkt
from shapely.geometry import Polygon
from data.plot_data import PlotData

import pandas
import tensorflow as tf
import numpy as np

# columns = ["is_rectangle", "is_flag", "is_trapezoid", "is_triangle", "plot_aspect_ratio", "plot_obb_ratio", "plot_interior_angle_sum"]
# undefined_shape_df = pandas.read_csv("data/preprocessed_data/UndefinedShape.csv")

# plot_shape_estimator = tf.keras.models.load_model("model/plot-shape-estimator.pb")

# test_data = PlotData(wkt.loads(undefined_shape_df.loc[0].plot_geometry_wkt))
# test_data = PlotData(Polygon([[-0.5,0], [2, 0.5], [1, 3], [0, 3]]))
test_data = PlotData(Polygon([[0, 0], [2, 0], [1, 3], [0, 3]]))
# test_series = np.array([[
#     test_data.is_rectangle, 
#     test_data.is_flag, 

#     test_data.is_trapezoid, 
#     test_data.is_triangle, 
#     test_data.plot_aspect_ratio, 
#     test_data.plot_obb_ratio, 
#     test_data.plot_interior_angle_sum
# ]])

# a=1