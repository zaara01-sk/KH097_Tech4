from typing import TypedDict, List, Dict, Any

class CitizenProfile(TypedDict):
    age: int
    occupation: str
    annual_income: int
    owns_land: bool
    taxpayer: bool
    enrolled_in_epfo_esic: bool
    secc_eligible: bool
    owns_pucca_house: bool
    documents: List[str]

class EligibilityCriteria(TypedDict, total=False):
    min_age: int
    max_age: int
    max_annual_income: int
    occupations: List[str]
    owns_land: bool
    taxpayer: bool
    enrolled_in_epfo_esic: bool
    owns_pucca_house: bool

class Scheme(TypedDict):
    id: str
    name: str
    category: str
    benefit_type: str
    annual_benefit_inr: int
    description: str
    eligibility: EligibilityCriteria
    conflicts_with: List[str]
    required_docs: List[str]