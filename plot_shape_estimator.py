from debugvisualizer.debugvisualizer import Plotter
from shapely.geometry import Polygon
from data.plot_data import PlotData
from utils.utils import ShapeLabel

from shapely.affinity import rotate, scale
import shapely

import tensorflow as tf
import numpy as np



class PlotShapeEstimator:
    shape_label = [shape_label.name for shape_label in ShapeLabel]
    estimator = tf.keras.models.load_model("model/plot-shape-estimator.pb")

    def estimate(self, plot: PlotData) -> str:
        self.plot = plot
        self.input_data = np.array(
            [
                [
                    plot.is_flag,
                    plot.is_rectangle,
                    plot.is_trapezoid,
                    plot.is_triangle,
                    plot.plot_aspect_ratio,
                    plot.plot_interior_angle_sum,
                    plot.plot_obb_ratio, 
                ]
            ]
        )
        
        return self.shape_label[self.estimator.predict(self.input_data).argmax()]
       
        
if __name__ == "__main__":
    plot_shape_estimator = PlotShapeEstimator()

    # trapezoid
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[0, 0], [2, 0], [1, 3], [0, 3]])
        )
    )
    
    print(f"predicted: {result}, expected: TrapezoidShape")
    

    # trapezoid
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[-0.5,0], [2, 0.5], [1, 3], [0, 3]])
        )
    )
    print(f"predicted: {result}, expected: TrapezoidShape")
    

    # square
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[0,0],[1,0],[1,1],[0,1]])
        )
    )
    print(f"predicted: {result}, expected: SquaredShape")


    # rotated square
    result = plot_shape_estimator.estimate(
        PlotData(
            rotate(Polygon([[0,0],[5,0],[5,5],[0,5]]), 15)
        )
    )
    print(f"predicted: {result}, expected: SquaredShape")


    # long-square
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[0,0],[5,0],[5,2],[0,2]])
        )
    )
    print(f"predicted: {result}, expected: LongSquaredShape")


    # long-square
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[0,0], [2,3], [1.5,4], [0,1.5]])
        )
    )
    print(f"predicted: {result}, expected: LongSquaredShape")
    

    # triangle
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[0,0], [2,2], [4,0]])
        )
    )
    print(f"predicted: {result}, expected: TriangleShape")


    # triangle
    result = plot_shape_estimator.estimate(
        PlotData(
            Polygon([[0,0], [2,2], [5.5,5], [3,0]])
        )
    )
    print(f"predicted: {result}, expected: TriangleShape")

    
    # flag
    result = plot_shape_estimator.estimate(
        PlotData(
            shapely.ops.unary_union([Polygon([[0,0], [0,5], [5,5], [5,0]]), Polygon([[0,5], [-5,5], [-5,4], [0,4]])])
        )
    )
    print(f"predicted: {result}, expected: FlagShape")
    
    
    # rotated flag
    result = plot_shape_estimator.estimate(
        PlotData(
            rotate(
                scale(
                    shapely.ops.unary_union(
                        [Polygon([[0,0], [0,5], [5,5], [5,0]]), Polygon([[0,5], [-5,5], [-5,4], [0,4]])]
                    ),
                    xfact=2
                ), 5
            )
        )
    )
    print(f"predicted: {result}, expected: FlagShape")