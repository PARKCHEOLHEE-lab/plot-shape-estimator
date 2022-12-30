from enum import Enum, auto
from typing import List, Tuple
from utils.consts import Consts
from debugvisualizer.debugvisualizer import Plotter
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiPoint

import shapely
import numpy as np

np.seterr(all='raise')


class ShapeLabel(Enum):
    """geometry's shape label"""
    SquareShape = 0
    LongSquareShape = auto()
    FlagShape = auto()
    TriangleShape = auto()
    TrapezoidShape = auto()
    UndefinedShape = auto()


def get_exploded_linestring(input_linestring: LineString) -> List[LineString]:
    """merged LineString to list of LineString"""
    exploded_linestring: List[LineString] = []
    linestring_vertices = MultiPoint(input_linestring.coords).geoms[:-1].geoms

    for vi in range(len(linestring_vertices)):
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
    return input_poly.area / input_poly.oriented_envelope.area


def get_linestring_slope(input_linestring: LineString) -> float:
    """get input liestring's slope"""
    x1, x2 = np.array(input_linestring.coords)[:, 0]
    y1, y2 = np.array(input_linestring.coords)[:, 1]
    
    slope = 0 if np.isclose(x2 - x1, 0) else (y2 - y1) / (x2 - x1) 
    return slope


def get_list_of_linestring_vertices(input_linestring: List[LineString]) -> List[Tuple[float]]:
    """convert list of linestring to list of vertices"""
    return [l.coords[0] for l in input_linestring]


def get_simplified_polygon(input_poly: Polygon) -> Polygon:
    """get simplified polygon"""
    exploded_input_poly = get_exploded_linestring(input_poly.boundary.simplify(Consts.TOLERANCE))
    
    simplified: List[LineString]
    simplified = [exploded_input_poly[0]]
    
    si = 0
    while si < len(exploded_input_poly):
        curr_segment = exploded_input_poly[si]
        prev_segment = simplified[-1]
        next_segment = simplified[0]
        
        is_last_si = si == len(exploded_input_poly) - 1
        
        is_needed_merge_curr_and_prev = (
            np.isclose(get_linestring_slope(curr_segment), get_linestring_slope(prev_segment), atol=Consts.TOLERANCE_SLOPE) 
            and not curr_segment.disjoint(prev_segment)
        )
        
        is_needed_merge_curr_and_next = (
            np.isclose(get_linestring_slope(curr_segment), get_linestring_slope(next_segment), atol=Consts.TOLERANCE_SLOPE) 
            and not curr_segment.disjoint(next_segment)
            and is_last_si
        )
        
        if is_needed_merge_curr_and_prev and is_needed_merge_curr_and_next:
            simplified.append(LineString([simplified[-1].coords[0], simplified[0].coords[-1]]))
            del simplified[0]
            del simplified[-2]

        elif is_needed_merge_curr_and_prev:
            simplified[-1] = LineString([prev_segment.coords[0], curr_segment.coords[-1]])
            
        elif is_needed_merge_curr_and_next:
            simplified.append(LineString([curr_segment.coords[0], next_segment.coords[-1]]))
            del simplified[0]
            
        else:
            simplified.append(curr_segment)
        
        si += 1
        
    if not shapely.ops.linemerge(simplified).is_simple:
        raise Exception("'simplified' is self-intersecting geometry")
    
    return Polygon(get_list_of_linestring_vertices(simplified))


def get_longest_segment(input_poly: Polygon) -> LineString:
    """get input polygon's longest segment"""
    return sorted(get_exploded_linestring(input_poly.boundary), key=lambda s: s.length, reverse=True)[0]


def get_angle_between_three_points(three_points: List[Tuple[float]]) -> float:
    """get angle between three points"""
    if len(three_points) != 3:
        raise Exception("'three_points' length is not 3")
    
    p1, p2, p3 = [np.array(p) for p in three_points]
    p1_p2 = p1 - p2
    p3_p2 = p3 - p2

    cosine_angle = np.dot(p1_p2, p3_p2) / (np.linalg.norm(p1_p2) * np.linalg.norm(p3_p2))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


def get_interior_angle_sum(input_poly: Polygon) -> float:
    """sum of input polygon's interior angles"""
    exploded_input_poly = get_exploded_linestring(input_poly.boundary)
    angle_sum = 0
    for si in range(len(exploded_input_poly)):
        curr_segment = exploded_input_poly[si]
        next_segment = exploded_input_poly[(si + 1) % len(exploded_input_poly)]
        
        union_segment = shapely.ops.linemerge(curr_segment.union(next_segment))
        if not isinstance(union_segment, LineString):
            raise Exception("'union_segment' type is not LineString")
        
        angle_sum += get_angle_between_three_points(union_segment.coords)
        
    return angle_sum


def get_estimated_shape_label(input_poly: Polygon, obb_ratio: float, aspect_ratio: float, interior_angle_sum: float) -> int:
    """get estimated input polygon's shape label"""
    is_satisfied_rectangle_obb_ratio = obb_ratio >= Consts.RECTANGLE_OBB_RATIO_BASELINE
    is_rectangle = np.isclose(interior_angle_sum, Consts.RECTANGLE_ANGLE_SUM) and is_satisfied_rectangle_obb_ratio
    is_lte_aspect_ratio_baseline = aspect_ratio <= Consts.LONG_SQUARE_SHAPE_ASPECT_RATIO_BASELINE
    
    is_flag = False
    flag_checker = input_poly.convex_hull - input_poly
    if isinstance(flag_checker, Polygon) and not flag_checker.is_empty:
        is_flag = (
            np.isclose(get_interior_angle_sum(flag_checker), Consts.TRIANGLE_ANGLE_SUM) 
            and obb_ratio <= Consts.FLAG_OBB_RATIO_BASELINE
        )
        
    is_trapezoid = False
    trapezoid_checker = (input_poly.oriented_envelope - input_poly - input_poly.convex_hull).buffer(-Consts.TRAPEZOID_CHECKER_EROSION)
    if isinstance(trapezoid_checker, MultiPolygon):
        is_trapezoid = (
            len(trapezoid_checker.geoms) >= Consts.TRAPEZOID_CHECKER_TRIANGLE_COUNT
            and obb_ratio >= Consts.TRAPEZOID_OBB_RATIO_BASELINE
        )
    
    shape_label = ShapeLabel.UndefinedShape.value
    
    if is_rectangle or is_satisfied_rectangle_obb_ratio and not is_rectangle:
        shape_label = ShapeLabel.SquareShape.value if is_lte_aspect_ratio_baseline else ShapeLabel.LongSquareShape.value
    
    elif is_flag:
        shape_label = ShapeLabel.FlagShape.value
        
    elif is_trapezoid:
        shape_label = ShapeLabel.TrapezoidShape.value
    
    return shape_label