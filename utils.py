from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint

from typing import Union, List

import numpy as np


def _get_exploded_linestring(input_linestring: LineString) -> List[LineString]:
    """merged LineString to list of LineString 

    Args:
        input_linestring (LineString): merged LineString

    Returns:
        List[LineString]: list of LineString
    """

    linestring_vertices = MultiPoint(input_linestring.coords).geoms
    exploded_linestring: List[LineString] = []

    for vi in range(len(linestring_vertices)):
        curr_vertex = linestring_vertices[vi % len(linestring_vertices)] 
        next_vertex = linestring_vertices[(vi + 1) % len(linestring_vertices)]

        exploded_linestring.append(LineString([curr_vertex, next_vertex]))

    return exploded_linestring

def get_longest_segment(input_poly: Polygon) -> LineString:
    """_summary_

    Args:
        input_poly (Polygon): _description_

    Returns:
        _type_: _description_
    """
    return sorted(_get_exploded_linestring(input_poly.boundary), key=lambda s: s.length, reverse=True)[0]

def get_axis_aligned_bounding_box(input_poly: Union[MultiPolygon, Polygon]):
    return

def get_plot_aspect_ratio():
    return

def get_plot_ombr_ratio():
    return

def get_plot_filled_ratio():
    return