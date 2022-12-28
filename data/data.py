from typing import List, Tuple
from dataclasses import dataclass
from shapely.geometry import Polygon, LineString

import utils.utils as utils



@dataclass
class PlotData:
    """plot data save format class"""
    plot_geometry: Polygon
    
    def __post_init__(self):
        self.plot_geometry: Polygon = utils.get_simplified_polygon(self.plot_geometry)
        self.plot_longest_segment: LineString = utils.get_longest_segment(self.plot_geometry)
        self.plot_interior_angle_sum: float = utils.get_interior_angle_sum(self.plot_geometry)
        self.plot_aspect_ratio: float = utils.get_aspect_ratio(self.plot_geometry)
        self.plot_obb_ratio: float = utils.get_obb_ratio(self.plot_geometry)
        self.plot_vertices_count: List[Tuple[float]] = len(self.plot_geometry.boundary.coords)