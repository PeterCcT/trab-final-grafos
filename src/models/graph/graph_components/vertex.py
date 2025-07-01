from enum import StrEnum
from typing import Any


class VertexInfoTypes(StrEnum):
    WEIGHT = "weight"
    LABEL = "label"

Vertex = int
VertexInfo = dict[int, dict[VertexInfoTypes, Any]]