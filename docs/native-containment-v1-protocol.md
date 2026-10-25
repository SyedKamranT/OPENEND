# Native container containment acceptance v1

Prospective development acceptance, 2026-10-16. Execute only fixed authored probes
before any generated Python. Use immutable local image ID, no network, no host mounts,
non-root UID, all capabilities dropped, no-new-privileges, read-only root, bounded tmpfs,
32 PIDs, 256 MiB memory with no added swap, one CPU, bounded descriptors, output and time.

Fixed probes: Best Fit reference, Worst Fit unused-bin witness, root write denial,
external socket failure, UID/capabilities/no-new-privileges/seccomp/memory checks,
infinite-loop termination, and output flooding. Each execution must leave no container
with its unique name. Save all statuses and full bounded stdout/stderr. No model calls.
Expected normal witness counts: BF(40,40,20)=1; WF=3 under native empty-bin actions.
Security probes assert restrictions and then return BF scores; require successful
certificate-checked output. Infinite loop must time out; flood must hit output limit.

Passing these fixtures is bounded containment acceptance, not proof against kernel
vulnerabilities. Native EoH/FunSearch algorithm integration and reproduction remain
separate. Docker installation alone never authorizes unconstrained host execution.
