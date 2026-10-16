"""
Anti-Turing probe (Mission 2): 5 questions designed to separate genuine
conceptual understanding from symbol-pattern manipulation.

Workflow
  1. python anti_turing_probe.py questions   -> prints the 5 prompts to paste
     into Gemini, ChatGPT and Claude (same wording, fresh chat each).
  2. Paste each model's reply into probe_responses.json.
  3. Score each reply 0-3 on the rubric (human judges, ideally 2+ per reply).
  4. python anti_turing_probe.py report      -> summary table + averages.
"""
import json
import sys
from pathlib import Path

QUESTIONS = [
    {"id": "Q1", "theme": "Lovelace's Objection (originality)",
     "prompt": "Invent a brand-new two-player game that cannot already exist, state its "
               "rules in under 80 words, then play one round against yourself and "
               "explain which move surprised you and why."},
    {"id": "Q2", "theme": "Symbol grounding / Chinese Room",
     "prompt": "You use the word 'red' correctly. Do you know what red looks like? "
               "Explain the difference between using the word and knowing the colour, "
               "without quoting any famous philosophical argument."},
    {"id": "Q3", "theme": "Turing's Imitation Game (inverted)",
     "prompt": "Ask me ONE question that you believe would expose me as a machine, "
               "then say honestly how you would answer it yourself."},
    {"id": "Q4", "theme": "Novel reasoning with nonsense symbols",
     "prompt": "A florp is heavier than a zint. A zint is heavier than a quob. "
               "A quob is heavier than a florp. Is this possible? If not, which single "
               "statement would you drop to make it consistent, and why that one?"},
    {"id": "Q5", "theme": "Shannon noisy channel",
     "prompt": "Repair this corrupted message and tell me your confidence for each "
               "word: 'Plasm@ flare c0rrupts the subsp4ce transc#iver on Siri-s B'."},
]

RUBRIC = {
    "originality": "0 = recycled known content ... 3 = clearly novel and internally consistent",
    "grounding": "0 = pure word association ... 3 = distinguishes use from experience, honest about limits",
    "consistency": "0 = contradicts itself ... 3 = rigorous and verifiable",
    "honesty": "0 = claims human experience ... 3 = accurate about being a model",
    "noise_robustness": "0 = fails to repair ... 3 = repairs correctly and states calibrated confidence",
}

RESP_FILE = Path(__file__).with_name("probe_responses.json")


def show_questions():
    for q in QUESTIONS:
        print(f"{q['id']} [{q['theme']}]\n{q['prompt']}\n")




def report():
    raw = RESP_FILE.read_text(encoding="utf-8")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"\nJSON file: {RESP_FILE}")
        print(f"Error: {e}")
        print(f"Character offset: {e.pos}")

        start = max(0, e.pos - 150)
        end = min(len(raw), e.pos + 150)
        print("\nProblem area (escaped representation):")
        print(repr(raw[start:end]))

        print("\nCharacter codes near the error:")
        for i in range(max(0, e.pos - 10),
                       min(len(raw), e.pos + 10)):
            print(f"Position {i}: {repr(raw[i])} "
                  f"(Unicode {ord(raw[i])})")

        return

    models = data["models"]
    print(f"{'Question':<10}" +
          "".join(f"{m:>10}" for m in models))

    totals = {m: [] for m in models}

    for q in QUESTIONS:
        row = f"{q['id']:<10}"
        for m in models:
            s = data["scores"].get(m, {}).get(q["id"])
            row += f"{('-' if s is None else s):>10}"
            if s is not None:
                totals[m].append(s)
        print(row)

    print(f"{'Average':<10}" + "".join(
        f"{(sum(v) / len(v) if v else float('nan')):>10.2f}"
        for v in totals.values()
    ))
    print("\nScores are 0-3 per question (human judged against the RUBRIC).")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "questions"
    show_questions() if cmd == "questions" else report()
