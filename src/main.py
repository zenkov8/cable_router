import argparse
import numpy as np
from building_model import BuildingModel
from grid import Grid
from pathfinder import PathFinder
from visualizer import Visualizer
from config import Config


def __parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cable routing in 3D building")

    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to building JSON model"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Source coordinates: x,y"
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Target coordinates: x,y"
    )

    return parser.parse_args()


def __parse_point(value: str, z: float) -> np.ndarray:
    x, y = map(float, value.split(","))
    return np.array([x, y, z], dtype=float)


def main() -> None:
    args = __parse_args()
    try:
        config = Config()
    except ValueError as e:
        print(f"CONFIG ERROR: {e}")
        return

    try:
        building = BuildingModel(args.model)
    except (ValueError, TypeError, FileNotFoundError) as e:
        print(f"BUILDING MODEL ERROR: {e}")
        return

    grid = Grid(building, config)
    grid.mark_ceiling()
    grid.mark_obstacles()

    max_z: float = float(building.ceiling.vertices[:, 2].max())

    source_point = __parse_point(args.source, max_z)
    target_point = __parse_point(args.target, max_z)

    try:
        pathfinder = PathFinder(grid)
        path_points = pathfinder.find_path(source_point, target_point)
    except (TypeError, ValueError) as e:
        print(f"PATHFINDER ERROR: {e}")
        return

    visualizer = Visualizer()
    visualizer.add_ceiling(building.ceiling)
    visualizer.add_obstacles(building.obstacles)
    visualizer.add_points([source_point, target_point])
    visualizer.add_cable(path_points, config.width)
    visualizer.add_key_events()
    visualizer.show()


if __name__ == "__main__":
    main()
