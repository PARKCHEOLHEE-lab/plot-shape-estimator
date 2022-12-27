from typing import Union, List
from debugvisualizer.debugvisualizer import Plotter
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint


def get_exploded_linestring(input_linestring: LineString) -> List[LineString]:
    """merged LineString to list of LineString"""
    linestring_vertices = MultiPoint(input_linestring.coords).geoms
    exploded_linestring: List[LineString] = []

    for vi in range(len(linestring_vertices) - 1):
        curr_vertex = linestring_vertices[vi % len(linestring_vertices)] 
        next_vertex = linestring_vertices[(vi + 1) % len(linestring_vertices)]

        exploded_linestring.append(LineString([curr_vertex, next_vertex]))

    return exploded_linestring


def get_aspect_ratio(input_poly: Polygon) -> float:
    """get input polygon's obb aspect ratio"""
    s1, _, s3, _ = sorted(get_exploded_linestring(input_poly.oriented_envelope.boundary), key=lambda l: l.length)
    return s3.length / s1.length


def get_obb_ratio(input_poly: Polygon) -> float:
    """get input polygon's obb ratio"""
    return input_poly.oriented_envelope.area / input_poly.area


# def get_longest_segment(input_poly: Polygon) -> LineString:
#     """get input polygon's longest segment"""
#     return sorted(get_exploded_linestring(input_poly.boundary), key=lambda s: s.length, reverse=True)[0]


# def get_plot_filled_ratio():
#     return


# def get_axis_aligned_bounding_box(input_poly: Union[MultiPolygon, Polygon]):
#     return