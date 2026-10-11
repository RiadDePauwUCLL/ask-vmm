import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.qa import VMMQA


ANSWERABLE_CASES = [
    {
        "question": "Wat is het onderwerp van het persbericht over de Maas?",
        "gold_facts": ["voorkomt dubbel werk"],
        "source": "gemeenschappelijke_maas_waterkwaliteit.pdf",
        "gold_page": 1,
    },
    {
        "question": "Wat is het doel van de campagne in Kortrijk?",
        "gold_facts": ["actuele luchtkwaliteitssituatie"],
        "source": "luchtkwaliteitsmeetcampagne_2021.pdf",
        "gold_page": 1,
    },
    {
        "question": "Voor welke doelgroep is het educatief pakket gemaakt?",
        "gold_facts": ["basisonderwijs"],
        "source": "educatief_pakket_luchtkwaliteit.pdf",
        "gold_page": 4,
    },
    {
        "question": "Wat is de BelAQI-index?",
        "gold_facts": ["1 tot 10"],
        "source": "beltair_persbericht.pdf",
        "gold_page": 1,
    },
    {
        "question": "In welke omgeving brengt de Kortrijkse campagne de luchtkwaliteit in kaart?",
        "gold_facts": ["hoog kortrijk"],
        "source": "luchtkwaliteitsmeetcampagne_2021.pdf",
        "gold_page": 1,
    },
    {
        "question": "Aan wie wordt de waterkwaliteitsinformatie over de Maas gerapporteerd?",
        "gold_facts": ["europese commissie"],
        "source": "gemeenschappelijke_maas_waterkwaliteit.pdf",
        "gold_page": 1,
    },
    {
        "question": "Volgens welke richtlijn wordt de Maas-informatie gerapporteerd?",
        "gold_facts": ["kaderrichtlijn water"],
        "source": "gemeenschappelijke_maas_waterkwaliteit.pdf",
        "gold_page": 1,
    },
    {
        "question": "What scale does the BelAQI index use?",
        "gold_facts": ["1 tot 10"],
        "source": "beltair_persbericht.pdf",
        "gold_page": 1,
    },
    {
        "question": "Welke maatregelen worden in het pakket besproken?",
        "gold_facts": ["verschillende maatregelen"],
        "source": "educatief_pakket_luchtkwaliteit.pdf",
        "gold_page": 18,
    },
]

REFUSAL_CASES = [
    "Wat is de gemiddelde temperatuur in de Leie?",
    "Wat is het nitraatgehalte in de Leie in 2022?",
    "Welke meetpost ligt in Leuven?",
    "Wat is de gemiddelde neerslag in de Ardennen?",
    "Wat is de pH-waarde van de Noordzee in 2022?",
]


def run_eval():
    qa = VMMQA(ROOT / "data" / "reports")
    passed = 0
    answerable_passed = 0
    hit_at_3 = 0
    refusal_passed = 0

    for case in ANSWERABLE_CASES:
        answer, sources = qa.answer_question(case["question"])
        answer_text = answer.lower()
        source_names = [name for name, _ in sources]
        source_ok = any(
            name == case["source"] and page == case["gold_page"]
            for name, page in sources
        )
        grounded_page = any(
            chunk.doc_name == case["source"]
            and chunk.page_number == case["gold_page"]
            and all(fact.lower() in chunk.text.lower() for fact in case["gold_facts"])
            for chunk in qa.chunks
        )
        ok = not answer_text.startswith("ik weet het niet") and source_ok and grounded_page
        answerable_passed += int(ok)
        hit_at_3 += int(source_ok)
        passed += int(ok)
        print(f"Q: {case['question']}")
        print(f"A: {answer}")
        print(f"Sources: {sources}")
        print(f"Result: {'PASS' if ok else 'FAIL'}")
        print("---")

    for question in REFUSAL_CASES:
        answer, sources = qa.answer_question(question)
        ok = "ik weet het niet" in answer.lower() and not sources
        refusal_passed += int(ok)
        passed += int(ok)
        print(f"Q: {question}")
        print(f"A: {answer}")
        print(f"Sources: {sources}")
        print(f"Result: {'PASS' if ok else 'FAIL'}")
        print("---")

    total = len(ANSWERABLE_CASES) + len(REFUSAL_CASES)
    print(f"Summary: {passed}/{total} passed")
    print(f"Answerable fact accuracy: {answerable_passed}/{len(ANSWERABLE_CASES)}")
    print(f"Hit@3: {hit_at_3}/{len(ANSWERABLE_CASES)}")
    print(f"Refusal accuracy: {refusal_passed}/{len(REFUSAL_CASES)}")
    return passed, total


if __name__ == "__main__":
    run_eval()
