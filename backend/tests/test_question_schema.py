"""Phase 0a tests: the Question schema accepts valid questions and rejects broken ones.

Each failure-path case breaks exactly one field of the valid fixture, so a
failing test tells you which validator is missing.
"""

import copy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.schemas.question import Question

FIXTURES = Path(__file__).parent / "fixtures"


def load_yaml(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return yaml.safe_load(f)


@pytest.fixture
def valid_data() -> dict:
    return load_yaml("valid_question.yaml")


# ---------- happy path ----------

def test_valid_question_loads(valid_data):
    q = Question.model_validate(valid_data)
    assert q.id == "beh-verification-01"
    assert q.type == "behavioral"
    assert len(q.probes) == 2
    assert len(q.rubric) == 3
    assert q.rubric[0].anchors[5].startswith("Deliberate")


def test_technical_type_also_valid(valid_data):
    valid_data["type"] = "technical"
    assert Question.model_validate(valid_data).type == "technical"


# ---------- failure path ----------

def test_missing_anchor_fixture_rejected():
    with pytest.raises(ValidationError):
        Question.model_validate(load_yaml("missing_anchor.yaml"))


def _set_type(d): d["type"] = "coding"
def _drop_anchor_3(d): del d["rubric"][0]["anchors"][3]
def _empty_anchor_text(d): d["rubric"][0]["anchors"][1] = "   "
def _zero_weight(d): d["rubric"][0]["weight"] = 0
def _zero_time_budget(d): d["time_budget_s"] = 0
def _zero_max_probes(d): d["max_probes"] = 0
def _empty_rubric(d): d["rubric"] = []
def _duplicate_criterion(d): d["rubric"][1]["criterion"] = d["rubric"][0]["criterion"]


@pytest.mark.parametrize(
    "breaker",
    [
        _set_type,
        _drop_anchor_3,
        _empty_anchor_text,
        _zero_weight,
        _zero_time_budget,
        _zero_max_probes,
        _empty_rubric,
        _duplicate_criterion,
    ],
    ids=lambda f: f.__name__.lstrip("_"),
)
def test_invalid_question_rejected(valid_data, breaker):
    data = copy.deepcopy(valid_data)
    breaker(data)
    with pytest.raises(ValidationError):
        Question.model_validate(data)