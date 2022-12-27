import numpy as np

from consts import Consts
from typing import Union, List, Tuple
from debugvisualizer.debugvisualizer import Plotter
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint



def get_exploded_linestring(input_linestring: LineString) -> List[LineString]:
    """merged LineString to list of LineString"""
    exploded_linestring: List[LineString] = []
    linestring_vertices = MultiPoint(input_linestring.coords).geoms

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


def get_linestring_slope(input_linestring: LineString) -> float:
    """get input liestring's slope"""
    x1, x2 = np.array(input_linestring.coords)[:, 0]
    y1, y2 = np.array(input_linestring.coords)[:, 1]
    return (y2 - y1) / (x2 - x1)


def get_list_of_linestring_vertices(input_linestring: List[LineString]) -> List[Tuple[float]]:
    """convert list of linestring to list of vertices"""
    return [l.coords[0] for l in input_linestring]


def get_simplified_polygon(input_poly: Polygon) -> Polygon:
    """get simplified polygon"""
    exploded_input_poly = get_exploded_linestring(input_poly.boundary)
    
    simplified: List[LineString]
    simplified = [exploded_input_poly[0]]
    
    si = 1
    is_needed_idx_add = False
    while si < len(exploded_input_poly) + 1:
        if is_needed_idx_add:
            si += 1
        
        curr_segment = exploded_input_poly[si % len(exploded_input_poly)]
        prev_segment = simplified[-1]
        
        is_last_si = si == len(exploded_input_poly)
        is_needed_merge = (
            np.isclose(get_linestring_slope(curr_segment), get_linestring_slope(prev_segment), atol=Consts.SLOPE) 
            and not curr_segment.disjoint(prev_segment)
        )
        
        if is_needed_merge:
            curr_segment = simplified[0] if is_last_si else curr_segment
            if is_last_si:
                del simplified[0]
            simplified[-1] = LineString([prev_segment.coords[0], curr_segment.coords[-1]])
            
        else:
            simplified.append(curr_segment)
        
        is_needed_idx_add = True
    
    return Polygon(get_list_of_linestring_vertices(simplified))


# def get_longest_segment(input_poly: Polygon) -> LineString:
#     """get input polygon's longest segment"""
#     return sorted(get_exploded_linestring(input_poly.boundary), key=lambda s: s.length, reverse=True)[0]


# def get_plot_filled_ratio():
#     return


# def get_axis_aligned_bounding_box(input_poly: Union[MultiPolygon, Polygon]):
#     return