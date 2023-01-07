from shapely.geometry import Polygon, LineString
from debugvisualizer.debugvisualizer import Plotter

import utils.utils as utils


class PlotData:
    """plot data save format class"""
    def __init__(self, plot_geometry: Polygon):
        self.__gen_properties(plot_geometry)
        
    def __gen_properties(self, plot_geometry: Polygon):
        """generate PlotData's all properties"""
        self.plot_geometry: Polygon
        self.plot_geometry = utils.get_simplified_polygon(plot_geometry)
        
        self.plot_aspect_ratio: float
        self.plot_aspect_ratio = utils.get_aspect_ratio(self.plot_geometry)
        
        self.plot_obb_ratio: float
        self.plot_obb_ratio = utils.get_obb_ratio(self.plot_geometry)
        
        self.plot_interior_angle_sum: float
        self.plot_interior_angle_sum = utils.get_interior_angle_sum(self.plot_geometry)
        
        self.plot_label: int
        self.is_rectangle: int
        self.is_flag: int
        self.is_trapezoid: int
        self.is_triangle: int
        
        (
            self.plot_label, 
            self.is_rectangle, 
            self.is_flag, 
            self.is_trapezoid, 
            self.is_triangle
        ) = utils.get_estimated_shape_label(
            self.plot_geometry, 
            self.plot_obb_ratio, 
            self.plot_aspect_ratio, 
            self.plot_interior_angle_sum
        )
        
        self.all_plot_data = [
            self.plot_aspect_ratio,
            self.plot_obb_ratio,
            self.plot_interior_angle_sum,
            self.plot_label,
            self.plot_geometry.wkt,
            self.is_rectangle,
            self.is_flag,
            self.is_trapezoid,
            self.is_triangle
        ]