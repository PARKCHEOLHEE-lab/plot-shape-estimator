from typing import List, Tuple
from dataclasses import dataclass
from shapely.geometry import Polygon, LineString
from debugvisualizer.debugvisualizer import Plotter

import utils.utils as utils



@dataclass
class PlotData:
    """plot data save format class"""
    plot_geometry: Polygon
    
    def __post_init__(self):
        """initialize"""
        self.__gen_properties()
            
    def __gen_properties(self):
        """generate PlotData's all properties"""
        self.plot_geometry: Polygon
        self.plot_geometry = utils.get_simplified_polygon(self.plot_geometry)
        
        self.plot_aspect_ratio: float
        self.plot_aspect_ratio = utils.get_aspect_ratio(self.plot_geometry)
        
        self.plot_obb_ratio: float
        self.plot_obb_ratio = utils.get_obb_ratio(self.plot_geometry)
        
        self.plot_interior_angle_sum: float
        self.plot_interior_angle_sum = utils.get_interior_angle_sum(self.plot_geometry)
        
        self.plot_label: int
        self.plot_label = utils.get_estimated_shape_label(
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
        ]