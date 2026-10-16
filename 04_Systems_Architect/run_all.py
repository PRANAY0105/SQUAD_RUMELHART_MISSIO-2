"""Integration demo: crew text -> noisy channel -> FST dialogue manager -> noisy channel -> crew."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "02_Protocol_Specialist"))
sys.path.insert(0, str(root / "03_Security_Sentinel"))

from fst_dialogue_manager import FSTDialogueManager
from noisy_channel_simulator import NoisyChannelSimulator, NOISE_VOCAB

LEXICON = {w: 1.0 for w in
           "hello aura status subsystem diagnose scan confirm yes no repair restore proceed goodbye".split()}


def main():
    fst = FSTDialogueManager()
    uplink = NoisyChannelSimulator(noise_rate=0.2, seed=7)
    downlink = NoisyChannelSimulator(noise_rate=0.2, seed=8)
    for msg in ["hello aura", "subsystem status", "yes", "yes", "proceed", "goodbye"]:
        up = uplink.transmit(msg)
        heard = uplink.decode(up, LEXICON)
        reply = fst.step(heard)
        down = downlink.transmit(reply)
        print(f"CREW  : {msg}\n  uplink  : {up.received}  -> decoded '{heard}'\n"
              f"  AURA  : {reply}  [{fst.state}]\n  downlink: {down.received}\n")


if __name__ == "__main__":
    main()
