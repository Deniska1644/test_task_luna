"""Миксины для сервисов: общие хелперы (построение дерева активностей)."""

from __future__ import annotations

from db.repo.activity import ActivityRepo


class ActivityTreeMixin:
    """Миксин для построения дерева активностей (id, name, children) из путей репозитория."""

    async def get_activity_paths_with_ids(
        self, leaf_ids: list[int], activity_repo: ActivityRepo
    ) -> list[list[tuple[int, str]]]:
        """Загружает пути от корня к листу из activity_ownership в виде списка (id, name) на путь."""
        return await activity_repo.get_paths_from_ownership(leaf_ids)

    @classmethod
    def build_activities_tree_with_ids(
        cls, paths: list[list[tuple[int, str]]]
    ) -> list[dict]:
        """Строит список корневых узлов из путей (корень → лист как (id, name)). Объединяет общих предков по id."""
        if not paths:
            return []
        nodes: dict[int, dict] = {}
        for path in paths:
            for i in range(len(path)):
                id_, name = path[i]
                if id_ not in nodes:
                    nodes[id_] = {"id": id_, "name": name, "children": []}
                if i < len(path) - 1:
                    child_id, child_name = path[i + 1]
                    if child_id not in nodes:
                        nodes[child_id] = {
                            "id": child_id,
                            "name": child_name,
                            "children": [],
                        }
                    if not any(c["id"] == child_id for c in nodes[id_]["children"]):
                        nodes[id_]["children"].append(nodes[child_id])
        seen_roots: set[int] = set()
        result: list[dict] = []
        for path in paths:
            root_id = path[0][0]
            if root_id not in seen_roots:
                seen_roots.add(root_id)
                result.append(nodes[root_id])
        return result
