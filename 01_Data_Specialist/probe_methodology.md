# Anti-Turing probe methodology (Data Specialist)

Goal: Test whether a model shows conceptual understanding or only pattern manipulation.

1. Run `python anti_turing_probe.py questions` and paste the 5 prompts, unchanged, into Gemini, Chat GPT and Claude (new chat each).
2. Record the full replies in `probe_responses.json`.
3. Two judges score each reply 0-3 on the rubric in `anti_turing_probe.py`; record the agreed score.
4. Run `python anti_turing_probe.py report` for the summary table.

Interpretation: high scores on Q1/Q4 argue against pure pattern-matching (Lovelace). Honest limits on Q2/Q3 matter more than human-sounding answers (Searle, Turing). Q5 links the probe to the noisy channel work.
Caveat: five questions are an illustration, not proof of understanding.
