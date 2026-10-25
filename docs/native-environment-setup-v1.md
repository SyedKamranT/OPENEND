# Native environment setup and crash recovery — 2026-10-16

Docker Desktop 4.95.0 is installed per-user. The official fresh installer matched
SHA-256 `73431db38491f770543880366228a23c993f84d1e8e045f56d83b8a98940cf76` and a valid
Docker Inc Authenticode signature. The crash-resumed file failed that checksum and
was not executed by the verification command. Both files and the setup report are
retained under `results/raw/native-environment-setup-v1`.

**Engine blocked:** Windows reports AMD Ryzen 5 3600 firmware virtualization disabled.
Docker/WSL report `HCS_E_HYPERV_NOT_INSTALLED`. The optional Windows component query
also requires administrator elevation, so its state remains unknown. No restart was
performed. The unusable Docker backend was asked to stop.

Owner action: enable CPU virtualization (AMD SVM/AMD-V) in BIOS/UEFI, then boot Windows.
In an administrator PowerShell, enable the WSL platform with
`wsl --install --no-distribution`, and restart if Windows requests it. Do not assume
firmware settings changed merely because the Windows command succeeded. Verify the
firmware flag and Docker Linux engine before running the prepared containment probes.

Installation reference: [Docker Windows setup](https://docs.docker.com/desktop/setup/install/windows-install/).
The user authorized selecting and provisioning the best local environment; this firmware
and restart requirement is a machine prerequisite, not an independent-review approval.

## Prepared implementation

- `native_runtime/`: evaluator image recipe, pinned NumPy, vector scoring over feasible
  bins including unused bins; never execute the worker against candidate code on the host.
- `src/openend/native_container.py`: immutable image ID, no host mounts/network, dropped
  capabilities, non-root user, bounded memory/PIDs/CPU/output/time, named-container cleanup.
- `src/openend/native_containment_audit.py`: seven predeclared reference/adversarial probes.
  These have **not run** because the engine is unavailable. Unit flag checks are not proof
  of isolation. Protocol: [native containment v1](native-containment-v1-protocol.md).
- `src/openend/native_prompts.py`: uses hash-pinned upstream EoH prompt builders and
  FunSearch prompt construction/code manipulation. Candidate code is parsed, never run.
  Six EoH operators and a recursive FunSearch fixture are saved in `results/raw/native-prompts-v1`.

Validation: **147 passed, one SciPy-dependent skip in 26.90s** under system Python.
The SciPy audit previously passed separately in the bundled numerical environment.
Ruff clean. Native prompt recursion/operator checks pass. No new model calls after crash.
Phase 4 remains open for containment and full native search/evaluator integration; no
scientific success or native reproduction is claimed from these component checks.
