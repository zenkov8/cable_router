from pathlib import Path
from typing import List, Tuple
import json
import numpy as np
import trimesh


class Loader:
    def __init__(self, json_path: Path) -> None:
        if not isinstance(json_path, Path):
            raise TypeError("JSON path must be a str or pathlib.Path object")
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        if not json_path.is_file():
            raise ValueError(f"JSON path is not a file: {json_path}")
        self.__json_path: Path = json_path
        self.__ceiling: trimesh.Trimesh | None = None
        self.__obstacles: List[trimesh.Trimesh] = []

    def load(self) -> Tuple[trimesh.Trimesh, List[trimesh.Trimesh]]:
        objects = self.__read_json()
        floor_meshes: List[trimesh.Trimesh] = []
        obstacles: List[trimesh.Trimesh] = []

        for obj in objects:
            mesh = self.__build_mesh(obj)
            category: str = obj.get("Category", "").lower()
            if "floor" in category:
                floor_meshes.append(mesh)
            else:
                obstacles.append(mesh)

        self.__ceiling = self.__get_ceiling_from_floor(floor_meshes)
        self.__obstacles = obstacles

        return self.__ceiling, self.__obstacles

    def __read_json(self) -> list:
        try:
            with open(self.__json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.__json_path}: {e}")
        except OSError as e:
            raise OSError(f"Error reading file {self.__json_path}: {e}")
        if not isinstance(data, list):
            raise ValueError(f"JSON root must be a list of objects, got {type(data)}")

        return data

    @staticmethod
    def __build_mesh(obj: dict) -> trimesh.Trimesh:
        if "Coords" not in obj or "Indices" not in obj:
            raise ValueError("Each object must contain 'Coords' and 'Indices' keys")

        coords = np.asarray(obj["Coords"], dtype=float).reshape((-1, 3))
        faces = np.asarray(obj["Indices"], dtype=int).reshape((-1, 3))
        if coords.size == 0:
            raise ValueError("Mesh has no vertices")
        if faces.size == 0:
            raise ValueError("Mesh has no faces")

        return trimesh.Trimesh(vertices=coords, faces=faces, process=False)

    @staticmethod
    def __get_ceiling_from_floor(floor_meshes: list[trimesh.Trimesh]) -> trimesh.Trimesh:
        if not floor_meshes:
            raise ValueError("No floor meshes provided")

        combined = trimesh.util.concatenate(floor_meshes)
        if combined.vertices.size == 0 or combined.faces.size == 0:
            raise ValueError("Combined floor mesh has no vertices or faces")

        z_max: float = float(combined.vertices[:, 2].max())
        face_mask = [np.allclose(combined.vertices[face][:, 2], z_max) for face in combined.faces]
        if not any(face_mask):
            raise ValueError("No ceiling faces detected at max Z")
        ceiling_faces = combined.faces[np.asarray(face_mask)]

        return trimesh.Trimesh(vertices=combined.vertices, faces=ceiling_faces, process=False)

