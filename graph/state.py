from typing import TypedDict, Optional, Dict

class QAState(TypedDict):
    test_case: str

    plan: Optional[Dict]
    last_action: Optional[Dict]
    last_action_result: Optional[Dict]
    screenshot_path: Optional[str]

    verdict: Optional[str]
    failure_type: Optional[str]
    notes: Optional[str]
    is_complete: Optional[bool]
    step: int
    max_steps: int

    # Optimization fields
    llm_calls: int  # Track total LLM calls
    no_change_count: int  # Track consecutive steps with no UI change

