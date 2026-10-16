# System architecture (Systems Architect)

crew utterance -> [uplink noisy channel] -> receiver decoder -> [FSTDialogueManager] -> AURA reply -> [downlink noisy channel] -> crew

| Component | Owner | File |
|---|---|---|
| Anti-Turing probe and scoring | Data Specialist | 01_Data_Specialist/anti_turing_probe.py |
| FSTDialogueManager | Protocol Specialist | 02_Protocol_Specialist/fst_dialogue_manager.py |
| NoisyChannelSimulator | Security Sentinel | 03_Security_Sentinel/noisy_channel_simulator.py |
| Integration demo | Systems Architect | 04_Systems_Architect/run_all.py |

Interfaces: the channel exchanges plain strings (max 7 words); the FST accepts a string and returns a string; both expose `.log` or `.history` for audit.
Finding: short inputs such as "yes" are erased entirely under noise, leaving the deterministic FST in place. A probabilistic layer or a retry protocol is needed.
