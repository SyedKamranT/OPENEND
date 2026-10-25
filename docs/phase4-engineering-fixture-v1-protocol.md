# Phase 4 deterministic integration acceptance

2026-10-16, before execution. Use phase4-engineering-v2 config unchanged and the three
existing adapters. Replace local inference with deterministic FF/BF/WF JSON responses,
including valid EoH thought strings. Report fixture calls separately from model calls.
This checks accounting, EoH operator cycling, FunSearch resets, protocol capture and
replay only. It cannot fill missing arms or measure proposal quality in the interrupted
live comparison. Require all 72 fixture responses accounted and exact offline replay.
