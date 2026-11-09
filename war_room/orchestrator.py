from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from war_room.agents import GreedyAttacker, IncidentResponder, SocAnalyst
from war_room.env.game_master import GameMaster


def run(seed: int = 7, max_turns: int = 12, live: bool = False) -> dict:
    root = Path(__file__).parent
    gm = GameMaster(root / "env" / "network.json", seed)
    attacker, soc, responder = GreedyAttacker(), SocAnalyst(), IncidentResponder()
    replay = []
    outcome = None
    for turn in range(1, max_turns + 1):
        gm.turn = turn
        attack = gm.apply_attack(attacker.choose(gm.attacker_view()))
        defender_view = gm.defender_view()
        assessment = soc.assess(defender_view)
        defense = responder.contain(assessment)
        if defense:
            gm.apply_defense(defense)
        replay.append({"turn": turn, "attack": asdict(attack), "soc_assessment": assessment, "defense": defense})
        if live:
            print(f"\n--- TURN {turn} ---")
            print(f"Game Master: {attack.message}")
            for alert in defender_view["alerts"]:
                print(f"Alert: {alert['message']}")
            print(f"SOC: {assessment['reason']}" if assessment else "SOC: no actionable alert")
            print(f"Response: {defense['action']} -> {defense['target']}" if defense else "Response: monitoring")
        gm.advance_turn()
        outcome = gm.outcome(max_turns)
        if outcome:
            break
    report = {
        "outcome": outcome or "in_progress", "turns": gm.turn, "compromised": sorted(gm.compromised), "stolen": sorted(gm.stolen),
        "detection_time": gm.first_detection_turn, "containment_time": gm.containment_turn,
        "score": {"data_lost": sum(gm.assets[item]["importance"] for item in gm.stolen), "business_downtime": len(gm.isolated) * 10},
        "timeline": [asdict(event) for event in gm.timeline], "replay": replay,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the safe fictional War Room simulation.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--turns", type=int, default=12)
    parser.add_argument("--output", type=Path, default=Path("artifacts/replay.json"))
    parser.add_argument("--live", action="store_true", help="Print the fog-of-war defender view each turn.")
    args = parser.parse_args()
    report = run(args.seed, args.turns, args.live)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Outcome: {report['outcome']} after {report['turns']} turn(s)")
    print(f"Detection: {report['detection_time']} | Containment: {report['containment_time']}")
    print(f"Replay written to {args.output}")


if __name__ == "__main__":
    main()
