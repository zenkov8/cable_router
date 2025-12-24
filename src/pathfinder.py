from typing import Dict, Tuple
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.csgraph import dijkstra
from grid import Grid


class PathFinder:
    def __init__(self, grid: Grid) -> None:
        self.__grid: Grid = grid
        self.__free_idx: np.ndarray = np.argwhere(self.__grid.obstacle_mask == 0)
        self.__idx_to_node: Dict[Tuple[int, int, int], int] = {tuple(idx): i for i, idx in enumerate(self.__free_idx)}
        self.__adj: lil_matrix | None = None

    @property
    def grid(self) -> Grid:
        return self.__grid

    @property
    def free_indices(self) -> np.ndarray:
        return self.__free_idx

    def __build_graph(self) -> None:
        n_nodes: int = self.__free_idx.shape[0]
        self.__adj = lil_matrix((n_nodes, n_nodes), dtype=np.float32)

        neighbors = np.array([
            [1, 0, 0], [-1, 0, 0],
            [0, 1, 0], [0, -1, 0],
            [0, 0, 1], [0, 0, -1]
        ])

        for i, idx in enumerate(self.__free_idx):
            for d in neighbors:
                nbr = tuple(idx + d)
                if nbr in self.__idx_to_node:
                    j = self.__idx_to_node[nbr]
                    self.__adj[i, j] = 1

    def find_path(self, source_point: np.ndarray, target_point: np.ndarray) -> np.ndarray:

        if self.__adj is None:
            self.__build_graph()

        source_idx = tuple(
            np.round((source_point - self.__grid.grid_min) / self.__grid.step).astype(int)
        )
        target_idx = tuple(
            np.round((target_point - self.__grid.grid_min) / self.__grid.step).astype(int)
        )
        if source_idx not in self.__idx_to_node:
            raise ValueError(
                f"Source point {source_point} is inside an obstacle or out of grid bounds"
            )
        if target_idx not in self.__idx_to_node:
            raise ValueError(
                f"Target point {target_point} is inside an obstacle or out of grid bounds"
            )

        source_node: int = self.__idx_to_node[source_idx]
        target_node: int = self.__idx_to_node[target_idx]

        dist_matrix, predecessors = dijkstra(
            csgraph=self.__adj,
            directed=False,
            indices=source_node,
            return_predecessors=True
        )

        if predecessors[target_node] == -9999:
            raise ValueError("Path not found")
        path_nodes = []
        cur: int = target_node
        while cur != -9999:
            path_nodes.append(self.__free_idx[cur])
            cur = predecessors[cur]
        path_nodes = np.array(path_nodes[::-1])
        path_points = self.__grid.grid_min + path_nodes * self.__grid.step

        return path_points
