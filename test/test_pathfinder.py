import pytest
import numpy as np
from src.grid import Grid
from src.pathfinder import PathFinder


class SimpleBuilding:
    def __init__(self, size=(10, 10, 5)):
        self.size = size
        self.ceiling = self
        self.obstacles = []
        self.vertices = np.array([[0, 0, size[2]], [size[0], 0, size[2]],
                                  [size[0], size[1], size[2]], [0, size[1], size[2]]])
        self.faces = [np.array([0, 1, 2, 3])]

    def get_bounds_xy(self):
        return np.array([0, 0]), np.array([self.size[0], self.size[1]])

    def get_bounds_z(self, offset=0):
        return 0, self.size[2]


class SimpleConfig:
    def __init__(self, step=1, offset=0, width=0):
        self.step = step
        self.offset = offset
        self.width = width


@pytest.fixture
def grid():
    building = SimpleBuilding()
    config = SimpleConfig()
    g = Grid(building, config)
    g.obstacle_mask[:] = 0
    return g


@pytest.fixture
def pathfinder(grid):
    return PathFinder(grid)

def test_pathfinder_basic(pathfinder):
    source = np.array([1, 1, 0])
    target = np.array([8, 8, 0])
    path = pathfinder.find_path(source, target)
    assert path.shape[0] > 0
    assert np.all(path[0] == source)
    assert np.all(path[-1] == target)

def test_target_in_obstacle(pathfinder, grid):
    grid.obstacle_mask[5, 5, 0] = 1
    pathfinder = PathFinder(grid)
    source = np.array([1, 1, 0])
    target = np.array([5, 5, 0])
    with pytest.raises(ValueError, match="Target point .* is inside an obstacle or out of grid bounds"):
        pathfinder.find_path(source, target)

def test_source_in_obstacle(pathfinder, grid):
    grid.obstacle_mask[2, 2, 0] = 1
    pathfinder = PathFinder(grid)
    source = np.array([2, 2, 0])
    target = np.array([7, 7, 0])
    with pytest.raises(ValueError, match="Source point .* is inside an obstacle or out of grid bounds"):
        pathfinder.find_path(source, target)

def test_no_path(grid):
    grid.obstacle_mask[:] = 1
    grid.obstacle_mask[0, 0, 0] = 0
    grid.obstacle_mask[1, 1, 0] = 0
    pf = PathFinder(grid)
    source = np.array([0, 0, 0])
    target = np.array([1, 1, 0])
    with pytest.raises(ValueError, match="Path not found"):
        pf.find_path(source, target)
