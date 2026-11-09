from __future__ import annotations

from typing import Any


class GreedyAttacker:
    """A replaceable baseline policy selecting only abstract, allowed actions."""

    def choose(self, state: dict[str, Any]) -> dict[str, str]:
        compromised = state["compromised"]
        if "db01" in compromised:
            return {"action": "exfiltrate_data", "target": "db01"}
        if not compromised:
            if "web01" not in state["isolated"]:
                return {"action": "exploit_web_app", "target": "web01"}
            if "laptop-amy" not in state["isolated"]:
                return {"action": "phish_employee", "target": "laptop-amy"}
            return {"action": "recon", "target": "web01"}
        source = compromised[0]
        if source not in state["privileged"]:
            return {"action": "escalate_privileges", "target": source}
        if source not in state.get("persistent", []):
            return {"action": "establish_persistence", "target": source}
        target = "db01" if source != "db01" else "dc01"
        return {"action": "move_laterally", "source": source, "target": target}


class SocAnalyst:
    def assess(self, view: dict[str, Any]) -> dict[str, str] | None:
        alerts = view["alerts"]
        ranked = {"high": 3, "medium": 2, "low": 1}
        credible = [alert for alert in alerts if "benign" not in alert["message"]]
        alert = max(credible, key=lambda item: ranked.get(item["details"].get("severity", "low"), 0), default=None)
        if not alert:
            return None
        return {"action": "investigate", "target": alert["details"]["host"], "reason": alert["message"], "severity": alert["details"].get("severity", "low")}


class IncidentResponder:
    def contain(self, assessment: dict[str, str] | None) -> dict[str, str] | None:
        if assessment and assessment["severity"] == "high":
            return {"action": "isolate_host", "target": assessment["target"], "reason": "Contain high-confidence alert"}
        if assessment and assessment["severity"] == "medium":
            return {"action": "block_ip", "target": "203.0.113.9", "reason": "Block source pending investigation"}
        return None
