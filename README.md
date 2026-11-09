# WarRoom Sentinel

> A safe, turn-based multi-agent cyber incident response simulation.

WarRoom Sentinel models a fictional company under attack. An abstract attacker advances through a simulated attack chain while a SOC and incident responder act under fog of war. Every asset, event, log, and outcome exists only in JSON game state—**the project never connects to, scans, or changes real systems**.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![Safety](https://img.shields.io/badge/Scope-fictional%20simulation-20c997) ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Highlights

- Fog of war: defenders see logs and alerts, not the attacker's action.
- Safe abstract stages: initial access, escalation, persistence, lateral movement, and exfiltration.
- A constrained action menu resolved by deterministic game rules.
- Reproducible incidents: the same seed always produces the same replay.
- Scores for detection time, containment time, business downtime, and data loss.
- A lightweight foundation for future JSON-constrained Ollama agents.

## Simulation loop

```text
Attacker action → Game Master resolves outcome and logs → SOC triage
       → Incident response action → Scribe replay and score
```

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/tabishsyed777/WarRoom-Sentinel.git
cd WarRoom-Sentinel
python3 -m war_room.orchestrator --seed 20 --turns 12 --live
```

The full turn replay is written to `artifacts/replay.json`.

```text
--- TURN 4 ---
Game Master: exploit_web_app against web01 succeeded
Alert: EDR alert: possible exploit_web_app on web01
SOC: EDR alert: possible exploit_web_app on web01
Response: isolate_host -> web01
```

Change the seed to explore another repeatable scenario:

```bash
python3 -m war_room.orchestrator --seed 42 --turns 15 --live
```

## Tests

No third-party dependencies are required.

```bash
python3 -m unittest discover -s tests -v
```

## Project structure

```text
war_room/
├── agents/            # Replaceable attacker, SOC, and responder policies
├── env/
│   ├── network.json   # Fictional assets, weaknesses, and defenses
│   └── game_master.py # Outcome resolution, logs, alerts, and scoring
└── orchestrator.py    # Turn loop, replay generation, and CLI
tests/                 # Deterministic simulation checks
```

## Safety model

This repository is a simulation, not a security tool.

- No exploit payloads, shell commands, scanners, real-network requests, or credential collection.
- Labels such as `exploit_web_app` are interpreted only by local `GameMaster` probability rules.
- All hosts and IP addresses are fictional; `203.0.113.9` is reserved for documentation examples.
- Only the Game Master can mutate the simulated world; agents select validated JSON actions.

## Roadmap

- [ ] CISO, threat-hunter, forensics, and communications roles
- [ ] MITRE ATT&CK technique labels for abstract events
- [ ] Scenario difficulty profiles and richer business-impact scoring
- [ ] Ollama-backed agents with JSON-only action validation
- [ ] Screenshot-ready dashboard and post-incident report export

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep all additions fictional, local, and simulation-only.

## License

Released under the [MIT License](LICENSE).
