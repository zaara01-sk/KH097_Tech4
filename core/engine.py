import json
import itertools
from typing import Dict, List, Tuple, Any

class SchemeEngine:
    def __init__(self, scheme_data_path: str = "data/schemes_data.json"):
        with open(scheme_data_path, "r", encoding="utf-8") as f:
            self.schemes: List[Dict[str, Any]] = json.load(f)
        self.scheme_map: Dict[str, Dict[str, Any]] = {s["id"]: s for s in self.schemes}

    def evaluate_eligibility(self, citizen: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        eligible = []
        ineligible = []

        for s in self.schemes:
            crit = s.get("eligibility", {})
            reasons = []

            # Age bounds check
            if "min_age" in crit and citizen.get("age", 0) < crit["min_age"]:
                reasons.append(f"Minimum required age is {crit['min_age']} (Applicant: {citizen.get('age')}).")
            if "max_age" in crit and citizen.get("age", 0) > crit["max_age"]:
                reasons.append(f"Maximum allowable age is {crit['max_age']} (Applicant: {citizen.get('age')}).")

            # Income cap check
            if "max_annual_income" in crit and citizen.get("annual_income", 0) > crit["max_annual_income"]:
                reasons.append(
                    f"Income limit is ₹{crit['max_annual_income']:,} (Applicant: ₹{citizen.get('annual_income'):,})."
                )

            # Occupation check
            if "occupations" in crit and citizen.get("occupation") not in crit["occupations"]:
                reasons.append(
                    f"Occupation '{citizen.get('occupation')}' not covered (Requires: {', '.join(crit['occupations'])})."
                )

            # Conditional checks
            if crit.get("owns_land", False) and not citizen.get("owns_land", False):
                reasons.append("Requires verified agricultural landholding.")
            if crit.get("enrolled_in_epfo_esic", None) is False and citizen.get("enrolled_in_epfo_esic", False):
                reasons.append("Applicant must NOT be an active EPFO/ESIC beneficiary.")
            if crit.get("taxpayer", None) is False and citizen.get("taxpayer", False):
                reasons.append("Applicant must be a non-taxpayer.")
            if crit.get("owns_pucca_house", None) is False and citizen.get("owns_pucca_house", False):
                reasons.append("Applicant already possesses a permanent (pucca) house.")

            if not reasons:
                eligible.append(s)
            else:
                ineligible.append({"scheme": s, "reasons": reasons})

        return eligible, ineligible

    def detect_conflicts(self, eligible_schemes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        eligible_ids = {s["id"] for s in eligible_schemes}
        conflicts = []
        checked = set()

        for s in eligible_schemes:
            for conf_id in s.get("conflicts_with", []):
                if conf_id in eligible_ids:
                    pair = tuple(sorted([s["id"], conf_id]))
                    if pair not in checked:
                        checked.add(pair)
                        conflicts.append({
                            "scheme_a": self.scheme_map[pair[0]]["name"],
                            "scheme_b": self.scheme_map[pair[1]]["name"],
                            "scheme_a_id": pair[0],
                            "scheme_b_id": pair[1],
                            "reason": f"Mutually exclusive benefit policies under national norms ({pair[0]} vs {pair[1]})."
                        })
        return conflicts

    def optimize_bundle(self, eligible_schemes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
        if not eligible_schemes:
            return [], [], 0

        # Construct adjacency graph for exclusions
        adj = {s["id"]: set() for s in eligible_schemes}
        for s in eligible_schemes:
            for conf_id in s.get("conflicts_with", []):
                if conf_id in adj:
                    adj[s["id"]].add(conf_id)
                    adj[conf_id].add(s["id"])

        best_bundle = ()
        max_total_value = -1
        scheme_ids = [s["id"] for s in eligible_schemes]
        n = len(scheme_ids)

        # Combinatorial search from largest subset downward
        for r in range(n, 0, -1):
            for combo in itertools.combinations(scheme_ids, r):
                conflict_exists = False
                for u, v in itertools.combinations(combo, 2):
                    if v in adj[u]:
                        conflict_exists = True
                        break

                if not conflict_exists:
                    current_value = sum(self.scheme_map[sid]["annual_benefit_inr"] for sid in combo)
                    if current_value > max_total_value:
                        max_total_value = current_value
                        best_bundle = combo

        selected_schemes = [self.scheme_map[sid] for sid in best_bundle]
        selected_ids = set(best_bundle)
        excluded_schemes = [s for s in eligible_schemes if s["id"] not in selected_ids]

        return selected_schemes, excluded_schemes, max(0, max_total_value)

    def generate_document_readiness(self, selected_bundle: List[Dict[str, Any]], citizen_docs: List[str]) -> Dict[str, Any]:
        all_required = set()
        scheme_doc_map = {}

        for s in selected_bundle:
            docs = s.get("required_docs", [])
            scheme_doc_map[s["name"]] = docs
            for doc in docs:
                all_required.add(doc)

        held_docs = set(citizen_docs)
        available = list(all_required.intersection(held_docs))
        missing = list(all_required.difference(held_docs))
        readiness_pct = (len(available) / len(all_required) * 100) if all_required else 100.0

        return {
            "all_required": list(all_required),
            "available": available,
            "missing": missing,
            "readiness_pct": round(readiness_pct, 1),
            "scheme_doc_map": scheme_doc_map
        }