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

HOLDOUT_ANSWERABLE_CASES = [
    {
        "question": "Welke NO2-grenswaarde werd volgens de modellering in 2016 overschreden?",
        "gold_facts": ["40 µg/m³"],
        "source": "luchtbeleidsplan_bijlage_4.pdf",
        "gold_page": 6,
    },
    {
        "question": "Welk percentage van de Vlaamse bevolking woonde in 2016 op een locatie met een overschrijding?",
        "gold_facts": ["3.7 %"],
        "source": "luchtbeleidsplan_bijlage_4.pdf",
        "gold_page": 6,
    },
    {
        "question": "Welk aandeel van het Vlaamse grondgebied werd volgens Tabel 2 overschreden?",
        "gold_facts": ["0,28 %"],
        "source": "luchtbeleidsplan_bijlage_4.pdf",
        "gold_page": 7,
    },
    {
        "question": "Welke sector levert de grootste Vlaamse bijdrage op stedelijk achtergrondniveau?",
        "gold_facts": ["transportsector"],
        "source": "luchtbeleidsplan_bijlage_4.pdf",
        "gold_page": 8,
    },
    {
        "question": "What model is used to calculate the NO2 concentrations?",
        "gold_facts": ["rio-ifdm-ospm"],
        "source": "luchtbeleidsplan_bijlage_4.pdf",
        "gold_page": 6,
    },
]

HOLDOUT_REFUSAL_CASES = [
    "What was the average temperature in the Leie?",
    "Wat was de PM10-concentratie in Brussel in 2024?",
    "Hoeveel regen viel er in Antwerpen in 2023?",
]


def evaluate_answerable_case(qa, case):
    answer, sources = qa.answer_question(case["question"])
    answer_text = answer.lower()
    source_ok = any(
        name == case["source"] and page == case["gold_page"]
        for name, page in sources
    )
    answer_facts_ok = all(fact.lower() in answer_text for fact in case["gold_facts"])
    grounded_page = any(
        chunk.doc_name == case["source"]
        and chunk.page_number == case["gold_page"]
        and all(fact.lower() in chunk.text.lower() for fact in case["gold_facts"])
        for chunk in qa.chunks
    )
    return answer, sources, source_ok, answer_facts_ok, grounded_page


def run_eval():
    qa = VMMQA(ROOT / "data" / "reports")
    passed = 0
    answerable_passed = 0
    hit_at_3 = 0
    answer_fact_passed = 0
    refusal_passed = 0

    for case in ANSWERABLE_CASES:
        answer, sources, source_ok, answer_facts_ok, grounded_page = evaluate_answerable_case(qa, case)
        ok = not answer.lower().startswith("ik weet het niet") and source_ok and answer_facts_ok and grounded_page
        answerable_passed += int(ok)
        hit_at_3 += int(source_ok)
        answer_fact_passed += int(answer_facts_ok)
        passed += int(ok)
        print(f"Q: {case['question']}")
        print(f"A: {answer}")
        print(f"Sources: {sources}")
        print(f"Result: {'PASS' if ok else 'FAIL'}")
        print("---")

    holdout_passed = 0
    holdout_answer_facts = 0
    for case in HOLDOUT_ANSWERABLE_CASES:
        answer, sources, source_ok, answer_facts_ok, grounded_page = evaluate_answerable_case(qa, case)
        ok = not answer.lower().startswith("ik weet het niet") and source_ok and answer_facts_ok and grounded_page
        holdout_passed += int(ok)
        holdout_answer_facts += int(answer_facts_ok)
        print(f"HOLDOUT Q: {case['question']}")
        print(f"A: {answer}")
        print(f"Sources: {sources}")
        print(f"Result: {'PASS' if ok else 'FAIL'}")
        print("---")

    holdout_refusals = 0
    for question in HOLDOUT_REFUSAL_CASES:
        answer, sources = qa.answer_question(question)
        ok = "ik weet het niet" in answer.lower() and not sources
        holdout_refusals += int(ok)
        print(f"HOLDOUT Q: {question}")
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

    passed += holdout_passed + holdout_refusals
    total = (
        len(ANSWERABLE_CASES)
        + len(REFUSAL_CASES)
        + len(HOLDOUT_ANSWERABLE_CASES)
        + len(HOLDOUT_REFUSAL_CASES)
    )
    print(f"Summary: {passed}/{total} passed")
    print(f"Answer fact accuracy: {answer_fact_passed}/{len(ANSWERABLE_CASES)}")
    print(f"Page retrieval accuracy: {hit_at_3}/{len(ANSWERABLE_CASES)}")
    print(f"Development refusal accuracy: {refusal_passed}/{len(REFUSAL_CASES)}")
    print(f"Holdout answer accuracy: {holdout_passed}/{len(HOLDOUT_ANSWERABLE_CASES)}")
    print(f"Holdout answer fact accuracy: {holdout_answer_facts}/{len(HOLDOUT_ANSWERABLE_CASES)}")
    print(f"Holdout refusal accuracy: {holdout_refusals}/{len(HOLDOUT_REFUSAL_CASES)}")
    return passed, total


if __name__ == "__main__":
    run_eval()
