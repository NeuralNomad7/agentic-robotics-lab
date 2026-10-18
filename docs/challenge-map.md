# Agentic robotics challenge map

This document connects each reference implementation to a production research question. It is intentionally opinionated: the purpose is to expose engineering judgment, not to catalog the entire field.

## 1. Open-ended models versus bounded physical authority

Vision-language-action models and LLM planners generalize by remaining flexible. A production robot still needs hard limits around velocity, force, workspace, proximity, authorization, and emergency state.

**Portfolio response:** Guardian is a model-independent enforcement point. The next step is a ROS 2 action adapter backed by signed policy bundles and hardware-specific safety controllers.

**Validation path:** property-based policy tests → simulator fault injection → hardware-in-the-loop → safety-case evidence.

## 2. Long-horizon reliability

One-shot success says little about a robot's ability to notice that the world diverged from its plan. Long-horizon deployment requires progress checks, replanning, recovery, and escalation.

**Portfolio response:** TaskForge makes recovery a first-class metric and prevents unsafe completion from looking successful.

**Validation path:** deterministic unit scenarios → seeded simulation perturbations → cross-environment suites → field replay.

## 3. Memory under a changing world

Retrieval alone is not enough. Physical facts become stale, sensors disagree, objects move, and provenance matters.

**Portfolio response:** World Memory keeps an append-only observation history and derives decayed beliefs at query time.

**Validation path:** synthetic contradictions → recorded sensor streams → spatial database backend → learned source calibration.

## 4. Coordination under partial failure

Multi-robot systems must handle heterogeneous capabilities, changing costs, network partitions, robot faults, and tasks abandoned mid-execution.

**Portfolio response:** FleetMind combines capability-aware bidding with expiring leases and heartbeat-driven reassignment.

**Validation path:** discrete-event simulation → async transport → packet-loss tests → mixed physical fleet.

## Adjacent challenges worth adding

- calibrated uncertainty across perception, planning, and control;
- sim-to-real evaluation with explicit coverage arguments;
- data governance and continual learning from fleet experience;
- human intent, oversight, and handoff design;
- latency and compute-aware model routing at the edge;
- semantic world models grounded in geometry and dynamics.

## Primary systems and benchmarks to study

- [RT-2](https://robotics-transformer2.github.io/) — web-scale vision-language knowledge transferred to robotic control.
- [Open X-Embodiment / RT-X](https://robotics-transformer-x.github.io/) — cross-embodiment datasets and generalist policies.
- [PaLM-E](https://palm-e.github.io/) — embodied multimodal language models.
- [BEHAVIOR-1K](https://behavior.stanford.edu/) — long-horizon household activity benchmark.
- [RoboCasa](https://robocasa.ai/) — large-scale simulation for everyday tasks.
- [LeRobot](https://github.com/huggingface/lerobot) — open models, datasets, and tooling for real-world robotics.

These references motivate the problem space; this repository does not claim reproduction or benchmark parity.
