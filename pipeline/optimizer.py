from typing import Dict, Any
from core.engine import SchemeEngine

class OptimizationPipeline:
    def __init__(self, engine: SchemeEngine):
        self.engine = engine

    def run(self, citizen_profile: Dict[str, Any]) -> Dict[str, Any]:
        eligible, ineligible = self.engine.evaluate_eligibility(citizen_profile)
        conflicts = self.engine.detect_conflicts(eligible)
        selected_bundle, excluded_by_conflict, total_benefit = self.engine.optimize_bundle(eligible)
        doc_metrics = self.engine.generate_document_readiness(
            selected_bundle, 
            citizen_profile.get("documents", [])
        )

        return {
            "eligible": eligible,
            "ineligible": ineligible,
            "conflicts": conflicts,
            "selected_bundle": selected_bundle,
            "excluded_by_conflict": excluded_by_conflict,
            "total_benefit": total_benefit,
            "doc_metrics": doc_metrics
        }