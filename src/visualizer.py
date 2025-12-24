from typing import Iterable, List
import numpy as np
import pyvista as pv
import trimesh
from cablegeometry import CableGeometry


class Visualizer:
    def __init__(self) -> None:
        self.__plotter: pv.Plotter = pv.Plotter()
        self.__ceiling_actor = None
        self.__obstacle_actors: List = []
        self.__cable_actors: List = []

    @property
    def plotter(self) -> pv.Plotter:
        return self.__plotter

    def add_ceiling(
        self,
        mesh: trimesh.Trimesh,
        color: str = "lightgray",
        opacity: float = 0.3
    ) -> None:
        self.__ceiling_actor = self.__plotter.add_mesh(
            mesh, color=color, opacity=opacity
        )

    def add_obstacles(
        self,
        meshes: Iterable[trimesh.Trimesh],
        color: str = "orange",
        opacity: float = 0.7
    ) -> None:
        for mesh in meshes:
            actor = self.__plotter.add_mesh(mesh, color=color, opacity=opacity)
            self.__obstacle_actors.append(actor)

    def add_cable(
        self,
        path_points: np.ndarray,
        width: float,
        height: float = 5.0,
        color: str = "red"
    ) -> None:
        boxes = CableGeometry.generate_cable_boxes(path_points, width, height)

        for box in boxes:
            cube = pv.Cube(**box)
            self.__plotter.add_mesh(cube, color=color)
            self.__cable_actors.append(cube)

    def add_points(
        self,
        points: Iterable[np.ndarray],
        color: str = "red",
        radius: float = 50.0
    ) -> None:
        for pt in points:
            self.__plotter.add_mesh(
                pv.Sphere(radius=radius, center=pt),
                color=color
            )

    def add_key_events(self) -> None:
        if self.__ceiling_actor:
            self.__plotter.add_key_event(
                "1",
                lambda: (
                    self.__ceiling_actor.SetVisibility(
                        not self.__ceiling_actor.GetVisibility()
                    ),
                    self.__plotter.render(),
                ),
            )

        if self.__obstacle_actors:
            self.__plotter.add_key_event(
                "2",
                lambda: (
                    [
                        actor.SetVisibility(not actor.GetVisibility())
                        for actor in self.__obstacle_actors
                    ],
                    self.__plotter.render(),
                ),
            )

        self.__plotter.add_text(
            "1 - Ceiling\n2 - Obstacles",
            position="upper_left",
            font_size=10
        )

    def show(self) -> None:
        self.__plotter.show()
