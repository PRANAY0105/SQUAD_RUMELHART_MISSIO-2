"""
FSTDialogueManager - deterministic dialogue control for AURA (Mission 2).

A dialogue manager modelled as a Mealy-style Finite State Transducer (FST):
    FST = (Q, Sigma, Gamma, delta, lambda, q0)
      Q      - dialogue states
      Sigma  - input symbols (intents recognised from the crew's utterance)
      Gamma  - output strings AURA may emit
      delta  - (state, input symbol) -> next state
      lambda - (state, input symbol) -> output string
      q0     - start state

Every step is deterministic: same state + same input => same output.
That is why it is a good foil for the probabilistic LLM probe: it
manipulates symbols by rule with no "understanding" (Lovelace's objection).
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Step:
    state_from: str
    symbol: str
    state_to: str
    output: str


class FSTDialogueManager:
    START = "IDLE"
    DEFAULT_SYMBOL = "unknown"

    # keyword rules for the input classifier (first match wins)
    INTENT_PATTERNS: List[Tuple[str, str]] = [
        ("bye",          r"\b(bye|goodbye|end|exit|quit|logout)\b"),
        ("greet",        r"\b(hello|hi|hey|greetings|aura)\b"),
        ("status_query", r"\b(status|integrity|subsystem|report|health)\b"),
        ("diagnose",     r"\b(diagnose|scan|check|analy[sz]e|radiation|sirius)\b"),
        ("repair",       r"\b(repair|restore|fix|recalibrate)\b"),
        ("confirm",      r"\b(yes|yep|confirm|affirmative|proceed|ok|okay)\b"),
        ("deny",         r"\b(no|nope|negative|cancel|abort|stop)\b"),
    ]

    LIVE_STATES = ("IDLE", "READY", "REPORTING", "DIAGNOSING", "REPAIR_WAIT", "REPAIRED")
    SYMBOLS = ("greet", "status_query", "diagnose", "repair", "confirm", "deny", "bye")

    def __init__(self) -> None:
        self.delta: Dict[Tuple[str, str], str] = {}
        self.lam: Dict[Tuple[str, str], str] = {}
        self.state: str = self.START
        self.history: List[Step] = []
        self._build_default_machine()

    # ---------- machine construction ----------
    def add_transition(self, state: str, symbol: str, next_state: str, output: str) -> None:
        self.delta[(state, symbol)] = next_state
        self.lam[(state, symbol)] = output

    def _build_default_machine(self) -> None:
        t = self.add_transition
        bye = "Goodbye. AURA standing by."
        wait = "Awaiting your command."
        # IDLE
        t("IDLE", "greet", "READY", "AURA online. Subsystem 02 at 7.1% integrity. How may I assist?")
        t("IDLE", "bye", "CLOSED", "Session closed.")
        # READY
        t("READY", "status_query", "REPORTING", "Subsystem 02: 7.1% of 14.2% target. Run diagnosis?")
        t("READY", "diagnose", "DIAGNOSING", "Scanning Sirius B plasma interference. Confirm to continue?")
        t("READY", "repair", "REPAIR_WAIT", "Repair requires a diagnosis first. Diagnose now?")
        t("READY", "greet", "READY", "Already online. " + wait)
        t("READY", "bye", "CLOSED", bye)
        # REPORTING
        t("REPORTING", "confirm", "DIAGNOSING", "Diagnosis started. Telemetry corrupted ~31%. Continue?")
        t("REPORTING", "deny", "READY", "Diagnosis skipped. " + wait)
        t("REPORTING", "bye", "CLOSED", bye)
        # DIAGNOSING
        t("DIAGNOSING", "confirm", "REPAIR_WAIT", "Fault found: transceiver phase drift. Begin repair?")
        t("DIAGNOSING", "repair", "REPAIR_WAIT", "Fault found: transceiver phase drift. Begin repair?")
        t("DIAGNOSING", "deny", "READY", "Diagnosis aborted. " + wait)
        t("DIAGNOSING", "bye", "CLOSED", bye)
        # REPAIR_WAIT
        t("REPAIR_WAIT", "confirm", "REPAIRED", "Repair complete. Subsystem 02 now 14.2% integrity.")
        t("REPAIR_WAIT", "repair", "REPAIRED", "Repair complete. Subsystem 02 now 14.2% integrity.")
        t("REPAIR_WAIT", "diagnose", "DIAGNOSING", "Re-scanning. Confirm to continue?")
        t("REPAIR_WAIT", "deny", "READY", "Repair cancelled. " + wait)
        t("REPAIR_WAIT", "bye", "CLOSED", bye)
        # REPAIRED
        t("REPAIRED", "status_query", "REPORTING", "Subsystem 02 at 14.2%. Run another diagnosis?")
        t("REPAIRED", "greet", "READY", "Welcome back. " + wait)
        t("REPAIRED", "bye", "CLOSED", "Mission log saved. Goodbye.")
        # Fallbacks: unknown input keeps the machine in place
        for s in self.LIVE_STATES:
            t(s, self.DEFAULT_SYMBOL, s, "Input not recognised. Please rephrase.")
        # CLOSED is absorbing
        t("CLOSED", self.DEFAULT_SYMBOL, "CLOSED", "Session closed. Restart required.")
        for sym in self.SYMBOLS:
            t("CLOSED", sym, "CLOSED", "Session closed. Restart required.")

    # ---------- introspection ----------
    @property
    def states(self) -> List[str]:
        return sorted({s for s, _ in self.delta} | set(self.delta.values()))

    @property
    def alphabet(self) -> List[str]:
        return sorted({a for _, a in self.delta})

    # ---------- runtime ----------
    def classify(self, utterance: str) -> str:
        """Map free text to an input symbol (first matching rule wins)."""
        text = utterance.lower()
        for symbol, pattern in self.INTENT_PATTERNS:
            if re.search(pattern, text):
                return symbol
        return self.DEFAULT_SYMBOL

    def step(self, utterance: str) -> str:
        symbol = self.classify(utterance)
        key = (self.state, symbol)
        if key not in self.delta:  # undefined pair -> fallback
            key = (self.state, self.DEFAULT_SYMBOL)
        nxt, out = self.delta[key], self.lam[key]
        self.history.append(Step(self.state, symbol, nxt, out))
        self.state = nxt
        return out

    def run(self, utterances: List[str]) -> List[str]:
        return [self.step(u) for u in utterances]

    def reset(self) -> None:
        self.state, self.history = self.START, []

    def transition_table(self) -> str:
        rows = ["state | input | next | output", "---|---|---|---"]
        for (s, a), n in sorted(self.delta.items()):
            rows.append(f"{s} | {a} | {n} | {self.lam[(s, a)]}")
        return "\n".join(rows)

    def to_dot(self) -> str:
        """Graphviz DOT export for the state diagram."""
        lines = ["digraph AURA_FST {", "  rankdir=LR;", "  start [shape=point];",
                 f"  start -> {self.START};"]
        for (s, a), n in sorted(self.delta.items()):
            if a != self.DEFAULT_SYMBOL:
                lines.append(f'  {s} -> {n} [label="{a}"];')
        lines.append("}")
        return "\n".join(lines)


if __name__ == "__main__":
    fst = FSTDialogueManager()
    for u in ["Hello AURA", "What is the subsystem status?", "yes", "yes", "proceed", "goodbye"]:
        print(f"CREW: {u}\nAURA: {fst.step(u)}   [{fst.state}]\n")
