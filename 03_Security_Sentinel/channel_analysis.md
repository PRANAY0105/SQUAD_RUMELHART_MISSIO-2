# Channel analysis (Security Sentinel)

## Constraints
- Max 7 words per turn, noise words included.
- At least 1 mandatory noise word injected per turn, leaving at most 6 payload words.

## Shannon capacity
C = B * log2(1 + S/N). With B = 100 Hz and SNR = 3 dB (S/N about 2.0), C is about 158 bit/s.
Plasma radiation lowers S/N, so capacity falls; no code can beat C at any error rate.

## Word-level model
Treat each payload word as a symbol that survives with probability 1 - p.
For a binary symmetric view, C = 1 - H(p): p = 0.25 gives 0.189 bit/use.
The simulator corrupts words by character swap, character drop, replacement with a noise word, or erasure.

## Mitigations tested
1. Compress first: drop stopwords so the 6 payload slots carry content words.
2. Receiver decoding: w* = argmax P(w) * P(obs | w), with a string-similarity likelihood.
3. Discard known noise-vocabulary words at the receiver.

## Reproduce
python noisy_channel_simulator.py
