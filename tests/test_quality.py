import json
from pathlib import Path

from app.agent import LabAgent


def test_expected_answer_keywords() -> None:
    agent = LabAgent()
    cases = [
        json.loads(line)
        for line in Path("data/expected_answers.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for index, case in enumerate(cases):
        result = agent.run(
            user_id="quality-test",
            session_id=f"quality-{index}",
            feature="qa",
            message=case["question"],
        )
        answer = result.answer.lower()
        assert all(keyword.lower() in answer for keyword in case["must_include"])
