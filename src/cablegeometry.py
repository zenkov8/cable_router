from typing import List, Dict
import numpy as np


class CableGeometry:
    @staticmethod
    def __collinear(
            p0: np.ndarray,
            p1: np.ndarray,
            p2: np.ndarray,
            tol: float = 1e-6
    ) -> bool:
        v1 = p1 - p0
        v2 = p2 - p1
        return np.linalg.norm(np.cross(v1, v2)) < tol

    @staticmethod
    def generate_cable_boxes(
        path_points: np.ndarray,
        width: float,
        height: float = 5.0
    ) -> List[Dict[str, np.ndarray | float]]:
        boxes: List[Dict[str, np.ndarray | float]] = []

        i: int = 0
        while i < len(path_points) - 1:
            source_idx: int = i
            target_idx: int = i + 1
            while (
                target_idx < len(path_points) - 1
                and CableGeometry.__collinear(
                    np.asarray(path_points[source_idx]),
                    np.asarray(path_points[target_idx]),
                    np.asarray(path_points[target_idx + 1])
                )
            ):
                target_idx += 1

            p1 = np.asarray(path_points[source_idx])
            p2 = np.asarray(path_points[target_idx])
            center: np.ndarray = (p1 + p2) / 2
            vec: np.ndarray = p2 - p1
            length: float = float(np.max(np.abs(vec)))

            if vec[0] != 0:
                box = {
                    "center": center,
                    "x_length": length,
                    "y_length": width,
                    "z_length": height,
                }
            elif vec[1] != 0:
                box = {
                    "center": center,
                    "x_length": width,
                    "y_length": length,
                    "z_length": height,
                }
            else:
                box = {
                    "center": center,
                    "x_length": height,
                    "y_length": width,
                    "z_length": length,
                }
            boxes.append(box)
            i = target_idx

            if i < len(path_points) - 2:
                p3 = np.asarray(path_points[i + 2])
                vec_next = p3 - p2

                if (
                    (vec[0] != 0 and vec_next[1] != 0)
                    or (vec[1] != 0 and vec_next[0] != 0)
                ):
                    corner_box = {
                        "center": p2,
                        "x_length": width,
                        "y_length": width,
                        "z_length": height,
                    }
                    boxes.append(corner_box)

        return boxes
