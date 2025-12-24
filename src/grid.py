from __future__ import annotations
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
from scipy.ndimage import binary_erosion
from typing import Tuple
from building_model import BuildingModel
from config import Config


class Grid:
    def __init__(self, building_model: BuildingModel, config: Config) -> None:
        self.__building = building_model
        self.__step: float = config.step
        self.__offset: float = config.offset
        self.__width: int = int(config.width // (2 * self.__step))
        min_xy, max_xy = self.__building.get_bounds_xy()
        min_z, max_z = self.__building.get_bounds_z(self.__offset)
        self.__grid_min: np.ndarray = np.array([*min_xy, min_z], dtype=float)
        self.__nx: int = int((max_xy[0] - min_xy[0]) // self.__step)
        self.__ny: int = int((max_xy[1] - min_xy[1]) // self.__step)
        self.__nz: int = int((max_z - min_z) // self.__step)
        self.__shape: Tuple[int, int, int] = (self.__nx + 1, self.__ny + 1, self.__nz + 1)
        self.__ceiling_mask: np.ndarray = self.__build_ceiling_mask()
        self.__obstacle_mask: np.ndarray = np.ones(self.__shape, dtype=np.uint8)

    @property
    def obstacle_mask(self) -> np.ndarray:
        return self.__obstacle_mask

    @property
    def grid_min(self) -> np.ndarray:
        return self.__grid_min

    @property
    def step(self) -> float:
        return self.__step

    @property
    def nz(self) -> int:
        return self.__nz

    @property
    def nx(self) -> int:
        return self.__nx

    @property
    def ny(self) -> int:
        return self.__ny

    def __build_ceiling_mask(self) -> np.ndarray:
        polygons = []
        for face in self.__building.ceiling.faces:
            poly = Polygon(self.__building.ceiling.vertices[face, :2])
            if poly.is_valid and poly.area > 0:
                polygons.append(poly)
        merged = unary_union(polygons)

        xx, yy = np.meshgrid(
            self.__grid_min[0] + np.arange(self.__nx + 1) * self.__step,
            self.__grid_min[1] + np.arange(self.__ny + 1) * self.__step,
            indexing="ij",
        )

        inside = np.zeros(xx.shape, dtype=bool)
        if merged.geom_type == "Polygon":
            inside = contains_xy(merged, xx, yy)
        elif merged.geom_type == "MultiPolygon":
            for poly in merged.geoms:
                inside |= contains_xy(poly, xx, yy)
        inside = binary_erosion(
            inside,
            structure=np.ones((2 * self.__width + 1, 2 * self.__width + 1)),
        )

        return inside

    def mark_ceiling(self) -> None:
        self.__obstacle_mask[:, :, self.__nz] = np.where(
            self.__ceiling_mask, 0, self.__obstacle_mask[:, :, self.__nz]
        )

    def obstacle_bbox_indices(
        self, obs: object, off: int
    ) -> Tuple[int, int, int, int, int]:
        idxs = np.floor((obs.vertices - self.__grid_min) // self.__step).astype(int)
        xmin, ymin, zmin = idxs.min(axis=0)
        xmax, ymax, _ = idxs.max(axis=0)
        xmin -= off + self.__width
        ymin -= off + self.__width
        xmax += off + self.__width
        ymax += off + self.__width
        zmin -= off

        return xmin, ymin, zmin, xmax, ymax

    def clip_bbox(
        self, xmin: int, ymin: int, zmin: int, xmax: int, ymax: int
    ) -> Tuple[int, int, int, int, int]:
        xmin_c = max(0, xmin)
        ymin_c = max(0, ymin)
        xmax_c = min(self.__nx, xmax)
        ymax_c = min(self.__ny, ymax)
        zmin_c = max(0, zmin)

        return xmin_c, ymin_c, zmin_c, xmax_c, ymax_c

    def mark_obstacles(self) -> None:
        off = int(self.__offset // self.__step)

        for obs in self.__building.obstacles:
            xmin, ymin, zmin, xmax, ymax = self.obstacle_bbox_indices(obs, off)
            xmin_c, ymin_c, zmin_c, xmax_c, ymax_c = self.clip_bbox(
                xmin, ymin, zmin, xmax, ymax
            )

            if xmin - off >= 0:
                self.__obstacle_mask[xmin_c, ymin_c:ymax_c + 1, zmin:self.__nz + 1] = 0
            if xmax + off <= self.__nx:
                self.__obstacle_mask[xmax_c, ymin_c:ymax_c + 1, zmin:self.__nz + 1] = 0
            if ymin - off >= 0:
                self.__obstacle_mask[xmin_c:xmax_c + 1, ymin_c, zmin:self.__nz + 1] = 0
            if ymax + off <= self.__ny:
                self.__obstacle_mask[xmin_c:xmax_c + 1, ymax_c, zmin:self.__nz + 1] = 0

            self.__obstacle_mask[xmin_c:xmax_c + 1, ymin_c:ymax_c + 1, zmin] = 0

        for obs in self.__building.obstacles:
            xmin, ymin, zmin, xmax, ymax = self.clip_bbox(
                *self.obstacle_bbox_indices(obs, off)
            )
            self.__obstacle_mask[
                xmin + 1:xmax,
                ymin + 1:ymax,
                zmin + 1:self.__nz + 1,
            ] = 1
