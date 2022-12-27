import utils
from dataclasses import dataclass
from shapely.geometry import Polygon



@dataclass
class PlotData:
    """plot data save format class"""
    plot_geometry: Polygon
    
    def __post_init__(self):
        self.plot_area = self.plot_geometry.area
        self.plot_aspect_ratio = utils.get_aspect_ratio(self.plot_geometry)
        self.plot_obb_ratio = utils.get_obb_ratio(self.plot_geometry)
        self.plot_geometry = utils.get_simplified_polygon(self.plot_geometry)