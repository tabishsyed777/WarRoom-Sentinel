from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Event:
    turn: int
    kind: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class GameMaster:
    """Resolves abstract game actions. It never touches real infrastructure."""

    def __init__(self, network_path: Path, seed: int | None = None) -> None:
        world = json.loads(network_path.read_text())
        self.assets = {asset["id"]: asset for asset in world["assets"]}
        self.defenses = world["defenses"]
        self.rng = random.Random(seed)
        self.turn = 0
        self.compromised: set[str] = set()
        self.privileged: set[str] = set()
        self.persistent: dict[str, int] = {}
        self.ever_compromised = False
        self.isolated: set[str] = set()
        self.stolen: set[str] = set()
        self.blocked_ips: set[str] = set()
        self.logs: list[Event] = []
        self.timeline: list[Event] = []
        self.first_detection_turn: int | None = None
        self.containment_turn: int | None = None

    def attacker_view(self) -> dict[str, Any]:
        return {"assets": list(self.assets.values()), "compromised": sorted(self.compromised), "privileged": sorted(self.privileged), "persistent": sorted(self.persistent), "isolated": sorted(self.isolated)}

    def defender_view(self) -> dict[str, Any]:
        return {"turn": self.turn, "logs": [asdict(event) for event in self.logs if event.turn == self.turn], "alerts": self._alerts()}

    def apply_attack(self, action: dict[str, str]) -> Event:
        name, target = action["action"], action["target"]
        source_ip = "203.0.113.9"
        success = False
        if name == "exploit_web_app" and target == "web01" and target not in self.isolated:
            success = self._roll(0.72)
        elif name == "phish_employee" and target == "laptop-amy" and target not in self.isolated:
            success = self._roll(0.58)
        elif name == "escalate_privileges" and target in self.compromised:
            success = self._roll(0.62)
        elif name == "move_laterally" and action.get("source") in self.compromised and target not in self.isolated:
            success = self._roll(0.55)
        elif name == "exfiltrate_data" and target in self.compromised and self.assets[target].get("crown_jewel"):
            success = self._roll(0.70)
        elif name == "establish_persistence" and target in self.compromised:
            success = self._roll(0.65)
        elif name == "recon":
            success = True

        if success and name == "exfiltrate_data":
            self.stolen.add(target)
        elif success and name == "escalate_privileges":
            self.privileged.add(target)
        elif success and name == "establish_persistence":
            self.persistent[target] = 0
        elif success:
            self.compromised.add(target)
            self.ever_compromised = True
        verb = "succeeded" if success else "failed"
        event = Event(self.turn, "attack", f"{name} against {target} {verb}", {"action": name, "target": target, "success": success})
        self.timeline.append(event)
        self.logs.extend(self._attack_logs(name, target, success, source_ip))
        return event

    def apply_defense(self, action: dict[str, str]) -> Event:
        name, target = action["action"], action.get("target", "")
        if name == "isolate_host" and target in self.assets:
            self.isolated.add(target)
            self.compromised.discard(target)
            self.privileged.discard(target)
            self.persistent.pop(target, None)
            if self.containment_turn is None:
                self.containment_turn = self.turn
        elif name == "block_ip":
            self.blocked_ips.add(target)
        elif name == "reset_credentials":
            self.compromised.discard(target)
            self.privileged.discard(target)
            self.persistent.pop(target, None)
        event = Event(self.turn, "defense", f"{name} applied to {target}", dict(action))
        self.timeline.append(event)
        return event

    def _attack_logs(self, name: str, target: str, success: bool, ip: str) -> list[Event]:
        messages = {
            "exploit_web_app": f"web01: unusual request pattern from {ip}",
            "phish_employee": "laptop-amy: suspicious email attachment opened",
            "escalate_privileges": f"{target}: privileged token anomaly",
            "move_laterally": f"{target}: remote authentication from internal host",
            "exfiltrate_data": f"{target}: abnormal outbound data transfer",
            "establish_persistence": f"{target}: unexpected startup configuration change",
            "recon": "perimeter telemetry: low-volume reconnaissance activity",
        }
        probability = 0.82 if self.assets[target].get("edr") else 0.28
        events = [Event(self.turn, "log", messages[name], {"host": target, "success": success})]
        if self._roll(probability):
            severity = "high" if success else "medium"
            events.append(Event(self.turn, "alert", f"EDR alert: possible {name} on {target}", {"host": target, "severity": severity}))
        return events

    def _alerts(self) -> list[dict[str, Any]]:
        alerts = [asdict(event) for event in self.logs if event.turn == self.turn and event.kind == "alert"]
        if self.rng.random() < 0.18:
            alerts.append(asdict(Event(self.turn, "alert", "EDR alert: benign software update anomaly", {"host": "laptop-amy", "severity": "low"})))
        if any(alert["details"].get("severity") in {"high", "medium"} for alert in alerts) and self.first_detection_turn is None:
            self.first_detection_turn = self.turn
        return alerts

    def _roll(self, chance: float) -> bool:
        return self.rng.random() < chance

    def outcome(self, max_turns: int) -> str | None:
        if "db01" in self.stolen:
            return "attacker_win"
        if any(age >= 3 for age in self.persistent.values()):
            return "attacker_win"
        if self.ever_compromised and not self.compromised:
            return "defender_win"
        if self.turn >= max_turns:
            return "defender_win" if "db01" not in self.stolen else "attacker_win"
        return None

    def advance_turn(self) -> None:
        """Age persistence after defenders have had their turn."""
        for host in self.persistent:
            self.persistent[host] += 1
