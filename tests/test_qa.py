import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.qa import VMMQA


@pytest.fixture(scope="module")
def qa():
    return VMMQA(ROOT / "data" / "reports")


def test_answers_question_with_citation(qa):
    answer, sources = qa.answer_question("Wat is de BelAQI-index?")

    assert "belaqi" in answer.lower()
    assert any(name == "beltair_persbericht.pdf" for name, _ in sources)


def test_refuses_unsupported_question(qa):
    answer, sources = qa.answer_question("Wat is de gemiddelde temperatuur in de Maas?")

    assert "ik weet het niet" in answer.lower()
    assert sources == []


def test_empty_question_is_refused(qa):
    answer, sources = qa.answer_question("   ")

    assert "ik weet het niet" in answer.lower()
    assert sources == []
