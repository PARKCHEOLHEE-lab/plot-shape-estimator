import utils
from dataclasses import dataclass
from shapely.geometry import Polygon



@dataclass
class PlotData:
    geometry: Polygon
    
    def __post_init__(self):
        self.plot_area = self.geometry.area
        self.plot_aspect_ratio = utils.get_aspect_ratio(self.geometry)
        self.plot_obb_ratio = utils.get_obb_ratio(self.geometry)