import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate import ANSWERABLE_CASES, REFUSAL_CASES
from src.qa import VMMQA

THRESHOLDS = (0.01, 0.02, 0.05, 0.10, 0.15, 0.20)


def is_refusal(answer, sources):
    return "ik weet het niet" in answer.lower() and not sources


def run_sweep():
    qa = VMMQA(ROOT / "data" / "reports")
    print("threshold,false_refusals,false_accepts")
    for threshold in THRESHOLDS:
        false_refusals = 0
        false_accepts = 0
        for case in ANSWERABLE_CASES:
            answer, sources = qa.answer_question(case["question"], threshold)
            false_refusals += int(is_refusal(answer, sources))
        for question in REFUSAL_CASES:
            answer, sources = qa.answer_question(question, threshold)
            false_accepts += int(not is_refusal(answer, sources))
        print(f"{threshold:.2f},{false_refusals},{false_accepts}")


if __name__ == "__main__":
    run_sweep()
