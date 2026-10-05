"""Question bank schema.

A Question is the contract shared by the interviewer (which asks it and picks
probes) and the evaluator (which grades against its rubric). Invalid questions
are rejected at load time so problems surface here, not as confusing scores
weeks later.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Every criterion must define at least these score anchors. Without concrete
# low/mid/high descriptions, the evaluator's scores drift between runs.
REQUIRED_ANCHORS = {1, 3, 5}


class StrictModel(BaseModel):
    # Reject unknown fields: a typo like `anchor:` instead of `anchors:` should
    # fail loudly rather than be silently dropped.
    model_config = ConfigDict(extra="forbid")


class Probe(StrictModel):
    """A follow-up the interviewer may ask, and the condition that warrants it."""

    trigger: str = Field(min_length=1)
    ask: str = Field(min_length=1)


class Criterion(StrictModel):
    """One graded dimension of an answer, with anchored score descriptions."""

    criterion: str = Field(min_length=1)
    # Weight 0 would silently drop the criterion from the total score.
    weight: int = Field(ge=1)
    anchors: dict[int, str]

    @field_validator("anchors")
    @classmethod
    def check_anchors(cls, anchors: dict[int, str]) -> dict[int, str]:
        missing = REQUIRED_ANCHORS - anchors.keys()
        if missing:
            raise ValueError(f"missing required anchors: {sorted(missing)}")
        blank = [score for score, text in anchors.items() if not text.strip()]
        if blank:
            raise ValueError(f"anchor text is empty for scores: {sorted(blank)}")
        return anchors


class Question(StrictModel):
    id: str = Field(min_length=1)
    # Literal, not str: the type selects the rubric style and probe behavior,
    # so an unknown type must never reach the interviewer.
    type: Literal["behavioral", "technical"]
    prompt: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    time_budget_s: int = Field(gt=0)
    max_probes: int = Field(gt=0)
    probes: list[Probe] = Field(default_factory=list)
    # A question with no criteria can't be evaluated.
    rubric: list[Criterion] = Field(min_length=1)
    # Stored with each evaluation so scores stay comparable as rubrics evolve.
    rubric_version: int = Field(ge=1)

    @model_validator(mode="after")
    def check_unique_criteria(self) -> "Question":
        # Model-level validator because it needs the whole rubric at once.
        # Duplicate names would overwrite each other's scores when keyed by name.
        names = [c.criterion for c in self.rubric]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            raise ValueError(f"duplicate criterion names: {sorted(duplicates)}")
        return self