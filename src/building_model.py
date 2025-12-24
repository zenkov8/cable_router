from pathlib import Path
from typing import List, Tuple
import numpy as np
import trimesh
from loader import Loader


class BuildingModel:
    def __init__(self, json_path: str | Path) -> None:
        self.__json_path: Path = Path(json_path)
        try:
            loader = Loader(self.__json_path)
            ceiling, obstacles = loader.load()
        except (FileNotFoundError, ValueError, TypeError, OSError) as e:
            print(f"LOADER ERROR: {e}")
            return

        if not isinstance(ceiling, trimesh.Trimesh):
            raise TypeError("Loader returned invalid ceiling mesh")
        if not isinstance(obstacles, list):
            raise TypeError("Loader returned invalid obstacles list")
        self.__ceiling: trimesh.Trimesh = ceiling
        self.__obstacles: List[trimesh.Trimesh] = obstacles

    @property
    def ceiling(self) -> trimesh.Trimesh:
        return self.__ceiling

    @property
    def obstacles(self) -> List[trimesh.Trimesh]:
        return self.__obstacles

    def get_bounds_xy(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.__ceiling.vertices.size == 0:
            raise ValueError("Ceiling mesh has no vertices")
        ceiling_xy = self.__ceiling.vertices[:, :2]

        if self.__obstacles:
            obs_vertices = []

            for obs in self.__obstacles:
                if obs.vertices.size == 0:
                    raise ValueError("Obstacle mesh has no vertices")
                obs_vertices.append(obs.vertices[:, :2])

            obs_xy = np.vstack(obs_vertices)
            min_xy = np.minimum(ceiling_xy.min(axis=0), obs_xy.min(axis=0))
            max_xy = np.maximum(ceiling_xy.max(axis=0), obs_xy.max(axis=0))
        else:
            min_xy = ceiling_xy.min(axis=0)
            max_xy = ceiling_xy.max(axis=0)

        return min_xy, max_xy

    def get_bounds_z(self, offset: float = 0.0) -> Tuple[float, float]:
        z_values = [self.__ceiling.vertices[:, 2]]

        for obs in self.__obstacles:
            if obs.vertices.size == 0:
                raise ValueError("Obstacle mesh has no vertices")
            z_values.append(obs.vertices[:, 2])

        min_z: float = min(z.min() for z in z_values) - offset
        max_z: float = self.__ceiling.vertices[:, 2].max()
        if min_z >= max_z:
            raise ValueError("Invalid Z bounds: min_z >= max_z")

        return min_z, max_z

