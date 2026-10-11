import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.qa import VMMQA

QUESTIONS = [
    {
        "question": "Wat is het onderwerp van het persbericht over de Maas?",
        "must_include": ["waterkwaliteit", "maas"],
        "source_hint": "gemeenschappelijke_maas_waterkwaliteit.pdf",
    },
    {
        "question": "Wat is het doel van de campagne in Kortrijk?",
        "must_include": ["luchtkwaliteit", "kortrijk"],
        "source_hint": "luchtkwaliteitsmeetcampagne_2021.pdf",
    },
    {
        "question": "Wat behandelt het educatief pakket over luchtkwaliteit?",
        "must_include": ["luchtkwaliteit", "pakket"],
        "source_hint": "educatief_pakket_luchtkwaliteit.pdf",
    },
    {
        "question": "Welke bron is het meest relevant voor een vraag over waterkwaliteit in de Maas?",
        "must_include": ["waterkwaliteit", "maas"],
        "source_hint": "gemeenschappelijke_maas_waterkwaliteit.pdf",
    },
    {
        "question": "Wat is de BelAQI-index?",
        "must_include": ["BelAQI", "luchtkwaliteit"],
        "source_hint": "beltair_persbericht.pdf",
    },
    {
        "question": "Wat worden voor de partikels in de luchtkwaliteitspakket besproken?",
        "must_include": ["luchtkwaliteit", "lucht"],
        "source_hint": "educatief_pakket_luchtkwaliteit.pdf",
    },
    {
        "question": "Hoe noemen ze de monitoring van waterkwaliteit in de Maas?",
        "must_include": ["monitoring", "waterkwaliteit"],
        "source_hint": "gemeenschappelijke_maas_waterkwaliteit.pdf",
    },
    {
        "question": "Wat wordt in de luchtkwaliteitscampagne in Kortrijk gemeten?",
        "must_include": ["stikstofdioxide", "luchtkwaliteit"],
        "source_hint": "luchtkwaliteitsmeetcampagne_2021.pdf",
    },
    {
        "question": "Wat is de gemiddelde temperatuur in de Maas?",
        "must_include": ["ik", "weet", "niet"],
        "source_hint": "no_answer",
    },
    {
        "question": "Waarover gaat de waterkwaliteitsinformatie voor de Maas?",
        "must_include": ["maas", "waterkwaliteit"],
        "source_hint": "gemeenschappelijke_maas_waterkwaliteit.pdf",
    },
]


def run_eval():
    qa = VMMQA(ROOT / "data" / "reports")
    passed = 0
    for item in QUESTIONS:
        question = item["question"]
        answer, sources = qa.answer_question(question)
        source_names = [name for name, _ in sources]
        answer_text = answer.lower()
        matched = [kw.lower() for kw in item["must_include"] if kw.lower() in answer_text]
        source_ok = item["source_hint"] in source_names or any(item["source_hint"] in name for name in source_names)
        ok = bool(matched) or source_ok
        print(f"Q: {question}")
        print(f"A: {answer}")
        print(f"Sources: {sources}")
        print(f"Result: {'PASS' if ok else 'FAIL'}")
        print("---")
        if ok:
            passed += 1

    total = len(QUESTIONS)
    print(f"Summary: {passed}/{total} passed")
    return passed, total


if __name__ == "__main__":
    run_eval()
