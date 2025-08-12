from __future__ import annotations

from typing import Protocol, Callable, Any


ProgressFn = Callable[[int, str], None]


class PipelineStage(Protocol):
    def run(self, ctx: dict[str, Any], progress: ProgressFn) -> None: ...


class Pipeline:
    def __init__(self, stages: list[PipelineStage]) -> None:
        self._stages = stages

    def run(self, ctx: dict[str, Any], progress: ProgressFn) -> dict[str, Any]:
        num_stages = max(1, len(self._stages))
        for index, stage in enumerate(self._stages, start=1):
            stage.run(ctx, progress)
            # Spread progress up to 95% across stages
            progress(min(95, int(index * 95 / num_stages)), f"stage:{index}:done")
        return ctx

from typing import Protocol, Callable, Any

ProgressFn = Callable[[int, str], None]

    