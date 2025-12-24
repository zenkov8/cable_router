import pytest
import numpy as np
from types import SimpleNamespace
from src.grid import Grid


@pytest.fixture
def simple_building():
    ceiling = SimpleNamespace(
        vertices=np.array([
            [0, 0, 10],
            [20, 0, 10],
            [20, 20, 10],
            [0, 20, 10]
        ]),
        faces=np.array([
            [0, 1, 2, 3]
        ])
    )

    obstacle = SimpleNamespace(
        vertices=np.array([
            [5, 5, 0],
            [10, 5, 0],
            [10, 10, 0],
            [5, 10, 0],
            [5, 5, 5],
            [10, 5, 5],
            [10, 10, 5],
            [5, 10, 5]
        ])
    )

    building = SimpleNamespace(
        ceiling=ceiling,
        obstacles=[obstacle],
        get_bounds_xy=lambda: (np.array([0, 0]), np.array([20, 20])),
        get_bounds_z=lambda offset: (0, 10 + offset)
    )
    return building

@pytest.fixture
def config():
    return SimpleNamespace(step=1, offset=2, width=1)

@pytest.fixture
def grid(simple_building, config):
    return Grid(simple_building, config)

def test_initialization(grid):
    assert grid.obstacle_mask.shape == (21, 21, 13)
    assert np.all(grid.obstacle_mask == 1)
    assert grid.step == 1
    assert grid.offset == 2
    assert grid.width == 0

def test_build_ceiling_mask(grid):
    mask = grid.ceiling_mask
    assert mask.shape == (grid.nx + 1, grid.ny + 1)
    assert np.any(mask) or np.any(~mask)

def test_mark_ceiling(grid):
    grid.mark_ceiling()
    top_layer = grid.obstacle_mask[:, :, grid.nz]
    assert top_layer.shape == (grid.nx + 1, grid.ny + 1)
    assert np.any(top_layer == 0)

def test_obstacle_bbox_indices(grid, simple_building):
    obs = simple_building.obstacles[0]
    off = int(grid.offset // grid.step)
    xmin, ymin, zmin, xmax, ymax = grid.obstacle_bbox_indices(obs, off)
    assert xmin <= 5 - (off + grid.width)
    assert xmax >= 10 + (off + grid.width)
    assert ymin <= 5 - (off + grid.width)
    assert ymax >= 10 + (off + grid.width)

def test_clip_bbox(grid):
    xmin, ymin, zmin, xmax, ymax = -5, -3, -1, 25, 22
    xmin_c, ymin_c, zmin_c, xmax_c, ymax_c = grid.clip_bbox(xmin, ymin, zmin, xmax, ymax)
    assert xmin_c >= 0
    assert ymin_c >= 0
    assert xmax_c <= grid.nx
    assert ymax_c <= grid.ny
    assert zmin_c >= 0

def test_mark_obstacles(grid):
    grid.mark_obstacles()
    off = int(grid.offset // grid.step)
    width = grid.width

    xmin_c = 5 - off - width + 1
    xmax_c = 10 + off + width
    ymin_c = 5 - off - width + 1
    ymax_c = 10 + off + width
    zmin_c = 0 - off + 1
    zmax_c = 5

    mask_c = grid.obstacle_mask[xmin_c:xmax_c, ymin_c:ymax_c, zmin_c:zmax_c+1]
    assert np.all(mask_c == 1)
    mask_layer = grid.obstacle_mask[(xmin_c-1):(xmax_c+1), (ymin_c-1):(ymax_c+1), (zmin_c-1):(zmax_c+1)]
    mask_outer = np.ones_like(mask_layer, dtype=bool)
    mask_outer[1:-1, 1:-1, 1:-1] = False
    assert np.all(mask_layer[mask_outer] == 0)
