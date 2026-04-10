"""Tasks router – GET /v1/tasks/{task_id} and GET /v1/graphs/{graph_id}."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from minigun.models.core import Task, TaskGraph

router = APIRouter(prefix="/v1", tags=["tasks"])
logger = logging.getLogger(__name__)

# In-memory store populated by the intents router (shared via module-level state)
# For a production system this would be backed by a database.
_task_store: dict[str, Task] = {}
_graph_store: dict[str, TaskGraph] = {}


def register_graph(graph: TaskGraph) -> None:
    """Register a graph and its tasks so they can be retrieved."""
    _graph_store[graph.id] = graph
    for task in graph.tasks:
        _task_store[task.id] = task


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str) -> Task:
    task = _task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@router.get("/graphs/{graph_id}", response_model=TaskGraph)
async def get_graph(graph_id: str) -> TaskGraph:
    graph = _graph_store.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Graph '{graph_id}' not found")
    return graph
