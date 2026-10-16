# AURA FST transition table

| state | input | next | output |
| ---|---|---|--- |
| CLOSED | bye | CLOSED | Session closed. Restart required. |
| CLOSED | confirm | CLOSED | Session closed. Restart required. |
| CLOSED | deny | CLOSED | Session closed. Restart required. |
| CLOSED | diagnose | CLOSED | Session closed. Restart required. |
| CLOSED | greet | CLOSED | Session closed. Restart required. |
| CLOSED | repair | CLOSED | Session closed. Restart required. |
| CLOSED | status_query | CLOSED | Session closed. Restart required. |
| CLOSED | unknown | CLOSED | Session closed. Restart required. |
| DIAGNOSING | bye | CLOSED | Goodbye. AURA standing by. |
| DIAGNOSING | confirm | REPAIR_WAIT | Fault found: transceiver phase drift. Begin repair? |
| DIAGNOSING | deny | READY | Diagnosis aborted. Awaiting your command. |
| DIAGNOSING | repair | REPAIR_WAIT | Fault found: transceiver phase drift. Begin repair? |
| DIAGNOSING | unknown | DIAGNOSING | Input not recognised. Please rephrase. |
| IDLE | bye | CLOSED | Session closed. |
| IDLE | greet | READY | AURA online. Subsystem 02 at 7.1% integrity. How may I assist? |
| IDLE | unknown | IDLE | Input not recognised. Please rephrase. |
| READY | bye | CLOSED | Goodbye. AURA standing by. |
| READY | diagnose | DIAGNOSING | Scanning Sirius B plasma interference. Confirm to continue? |
| READY | greet | READY | Already online. Awaiting your command. |
| READY | repair | REPAIR_WAIT | Repair requires a diagnosis first. Diagnose now? |
| READY | status_query | REPORTING | Subsystem 02: 7.1% of 14.2% target. Run diagnosis? |
| READY | unknown | READY | Input not recognised. Please rephrase. |
| REPAIRED | bye | CLOSED | Mission log saved. Goodbye. |
| REPAIRED | greet | READY | Welcome back. Awaiting your command. |
| REPAIRED | status_query | REPORTING | Subsystem 02 at 14.2%. Run another diagnosis? |
| REPAIRED | unknown | REPAIRED | Input not recognised. Please rephrase. |
| REPAIR_WAIT | bye | CLOSED | Goodbye. AURA standing by. |
| REPAIR_WAIT | confirm | REPAIRED | Repair complete. Subsystem 02 now 14.2% integrity. |
| REPAIR_WAIT | deny | READY | Repair cancelled. Awaiting your command. |
| REPAIR_WAIT | diagnose | DIAGNOSING | Re-scanning. Confirm to continue? |
| REPAIR_WAIT | repair | REPAIRED | Repair complete. Subsystem 02 now 14.2% integrity. |
| REPAIR_WAIT | unknown | REPAIR_WAIT | Input not recognised. Please rephrase. |
| REPORTING | bye | CLOSED | Goodbye. AURA standing by. |
| REPORTING | confirm | DIAGNOSING | Diagnosis started. Telemetry corrupted ~31%. Continue? |
| REPORTING | deny | READY | Diagnosis skipped. Awaiting your command. |
| REPORTING | unknown | REPORTING | Input not recognised. Please rephrase. |
