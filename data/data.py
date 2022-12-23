from dataclasses import dataclass
from shapely.geometry import Polygon



@dataclass
class PlotData:
    pnu: str
    uaa: str
    geometry: Polygon