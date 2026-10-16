"""
Noisy Channel Simulator (Mission 2) - Shannon's noisy channel for AURA's
subspace transceiver under Sirius B plasma radiation.

Hard rules enforced on EVERY transmitted turn:
  1. Bandwidth: at most MAX_WORDS (7) words per turn, noise words included.
  2. Noise vocabulary injection: at least MIN_NOISE (1) word from NOISE_VOCAB
     is mandatorily injected into every turn.

NOTE: NOISE_VOCAB below is a placeholder plasma-themed list. If the mission
brief supplies an official noise vocabulary, replace it (or load it with
load_noise_vocab('noise_vocabulary.txt')).

Pipeline:  message -> compress(<=7 - noise slots) -> corrupt -> inject -> receiver
Receiver:  noisy-channel decoding  w* = argmax_w P(w) * P(obs | w)
"""
from __future__ import annotations
import difflib
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

MAX_WORDS = 7
MIN_NOISE = 1
NOISE_VOCAB = ["plasma", "static", "flare", "quasar", "ion", "photon", "void", "sirius-b", "scatter"]
STOPWORDS = {"the", "a", "an", "of", "to", "is", "are", "and", "please", "that", "this", "it", "we"}


def load_noise_vocab(path: str) -> List[str]:
    with open(path, encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip() and not w.startswith("#")]


# ---------------- Shannon theory helpers ----------------
def shannon_capacity(bandwidth_hz: float, snr_db: float) -> float:
    """C = B * log2(1 + S/N)  [bits per second], SNR given in dB."""
    return bandwidth_hz * math.log2(1 + 10 ** (snr_db / 10))


def bsc_capacity(p: float) -> float:
    """Binary symmetric channel capacity C = 1 - H(p) bits per use."""
    if p in (0.0, 1.0):
        return 1.0
    return 1 + p * math.log2(p) + (1 - p) * math.log2(1 - p)


@dataclass
class Turn:
    original: str
    sent_words: List[str]
    received: str
    injected_noise: List[str]
    corrupted_positions: List[int]
    decoded: Optional[str] = None


class NoisyChannelSimulator:
    def __init__(self, noise_rate: float = 0.25, noise_vocab: Optional[List[str]] = None,
                 max_words: int = MAX_WORDS, min_noise: int = MIN_NOISE, seed: Optional[int] = None):
        if not 0 <= noise_rate <= 1:
            raise ValueError("noise_rate must be in [0, 1]")
        if min_noise >= max_words:
            raise ValueError("min_noise must be smaller than max_words")
        self.noise_rate = noise_rate
        self.noise_vocab = list(noise_vocab or NOISE_VOCAB)
        self.max_words = max_words
        self.min_noise = min_noise
        self.rng = random.Random(seed)
        self.log: List[Turn] = []

    # ---- stage 1: respect bandwidth (reserve slots for the noise words) ----
    def compress(self, message: str) -> List[str]:
        budget = self.max_words - self.min_noise
        words = message.split()
        if len(words) > budget:  # drop low-information words first
            words = [w for w in words if w.lower().strip(".,!?") not in STOPWORDS]
        return words[:budget]

    # ---- stage 2: channel corruption (word-level substitution/deletion) ----
    def _corrupt_word(self, w: str) -> Optional[str]:
        kind = self.rng.choice(["swap_char", "drop_char", "replace", "erase"])
        if kind == "erase":
            return None
        if kind == "replace":
            return self.rng.choice(self.noise_vocab)
        if len(w) < 2:
            return w
        i = self.rng.randrange(len(w))
        if kind == "drop_char":
            return w[:i] + w[i + 1:]
        return w[:i] + self.rng.choice("#@%&*?") + w[i + 1:]

    def transmit(self, message: str) -> Turn:
        words = self.compress(message)
        corrupted, positions = [], []
        for idx, w in enumerate(words):
            if self.rng.random() < self.noise_rate:
                positions.append(idx)
                new = self._corrupt_word(w)
                if new is not None:
                    corrupted.append(new)
            else:
                corrupted.append(w)
        # mandatory noise injection (always at least min_noise words)
        injected = [self.rng.choice(self.noise_vocab) for _ in range(self.min_noise)]
        for n in injected:
            corrupted.insert(self.rng.randint(0, len(corrupted)), n)
        corrupted = corrupted[: self.max_words]
        # re-assert injection if truncation or insertion pushed noise out
        if not any(w in self.noise_vocab for w in corrupted):
            corrupted[-1] = injected[0]
        turn = Turn(message, words, " ".join(corrupted), injected, positions)
        assert len(turn.received.split()) <= self.max_words, "bandwidth violated"
        assert any(w in self.noise_vocab for w in turn.received.split()), "no noise injected"
        self.log.append(turn)
        return turn

    # ---- stage 3: receiver decoding, w* = argmax P(w) P(obs|w) ----
    def decode(self, turn: Turn, lexicon: Dict[str, float]) -> str:
        """lexicon maps word -> prior probability P(w). Noise-vocab words are discarded."""
        out = []
        for obs in turn.received.split():
            if obs in self.noise_vocab:
                continue
            best, best_score = obs, 0.0
            for cand, prior in lexicon.items():
                likelihood = difflib.SequenceMatcher(None, obs.lower(), cand.lower()).ratio() ** 3
                score = prior * likelihood
                if score > best_score:
                    best, best_score = cand, score
            out.append(best)
        turn.decoded = " ".join(out)
        return turn.decoded

    def word_error_rate(self, turn: Turn) -> float:
        ref = [w.lower().strip(".,!?") for w in turn.sent_words]
        hyp = (turn.decoded or turn.received).lower().split()
        sm = difflib.SequenceMatcher(None, ref, hyp)
        matched = sum(b.size for b in sm.get_matching_blocks())
        return 1 - matched / max(len(ref), 1)


if __name__ == "__main__":
    lexicon = {w: 1 / 12 for w in
               "repair subsystem transceiver integrity restore telemetry diagnose radiation phase drift confirm scan".split()}
    sim = NoisyChannelSimulator(noise_rate=0.3, seed=42)
    msgs = ["Please repair the subsystem transceiver and restore integrity now",
            "Confirm radiation scan of telemetry phase drift"]
    for m in msgs:
        t = sim.transmit(m)
        sim.decode(t, lexicon)
        print(f"SENT    : {m}\nRECEIVED: {t.received}   ({len(t.received.split())} words)\n"
              f"DECODED : {t.decoded}   WER={sim.word_error_rate(t):.2f}\n")
    print("Shannon C (B=100 Hz, SNR=3 dB): %.1f bit/s" % shannon_capacity(100, 3))
    print("BSC capacity at p=0.25: %.3f bit/use" % bsc_capacity(0.25))
