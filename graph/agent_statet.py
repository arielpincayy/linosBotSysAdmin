from typing import TypedDict

class AgentState(TypedDict):
    user_request: str
    architect_instructions: str
    final_script: str
    verification_report: str
    needs_correction: bool
    correction_count: int
    corrected_script: str