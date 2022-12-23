from dataclasses import dataclass
from shapely.geometry import Polygon



@dataclass
class Plot:
    pnu: str
    uaa: str
    geometry: Polygon