from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    def __init__(self) -> None:
        self.__path: Path = Path(__file__).parent.parent / "data" / "config.yaml"
        self.__data: Dict[str, Any] = self.__load_yaml()
        self.__set_defaults()
        self.__bind_fields()

    @property
    def step(self) -> float:
        return self.__step

    @property
    def orientation(self) -> str:
        return self.__orientation

    @property
    def offset(self) -> float:
        return self.__offset

    @property
    def width(self) -> float:
        return self.__width

    def __load_yaml(self) -> Dict[str, Any]:
        if not self.__path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.__path}")
        with open(self.__path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def __set_defaults(self) -> None:
        self.__data.setdefault("grid", {})
        self.__data["grid"].setdefault("cell_size", 10)
        self.__data["grid"].setdefault("orientation", "xyz")
        self.__data.setdefault("routing", {})
        self.__data["routing"].setdefault("offset", 50)
        self.__data.setdefault("cable", {})
        self.__data["cable"].setdefault("width", 100)

    def __bind_fields(self):
        self.__step = float(self.__data["grid"]["cell_size"])
        if self.step <= 0:
            raise ValueError(f"Config error: grid.cell_size must be > 0, got {self.step}")
        self.__orientation = self.__data["grid"]["orientation"]
        if self.__orientation not in ("xyz", "xy", "xz", "yz"):
            raise ValueError(f"Config error: grid.orientation must be one of xyz/xy/xz/yz, got '{self.orientation}'")
        self.__offset = float(self.__data["routing"]["offset"])
        if self.offset < 0:
            raise ValueError(f"Config error: routing.offset must be >= 0, got {self.offset}")
        self.__width = float(self.__data["cable"]["width"])
        if self.width <= 0:
            raise ValueError(f"Config error: cable.width must be > 0, got {self.width}")

