from tools.llm import LLM

SUPERVISOR_PROMPT = """You are SUPERVISOR: a mobile QA verification agent.
You MUST output ONLY valid JSON.

Your job:
1. Evaluate if the test case is COMPLETE (all steps satisfied) or INCOMPLETE (needs more steps).
2. If complete, decide verdict (pass/fail).
3. Classify failures:
   - execution_failure: tool/ADB failed, or required UI element not found when planner says "cannot_find"
   - assertion_failure: steps executed successfully but expected condition is false (e.g., wrong color, wrong text)

Output schema:
{
  "verdict": "pass" | "fail" | "incomplete",
  "failure_type": "execution_failure" | "assertion_failure" | null,
  "notes": "concise explanation",
  "is_complete": true | false
}

Rules:
- If verdict is "incomplete", set is_complete=false
- If verdict is "pass" or "fail", set is_complete=true
- Only use "execution_failure" if the tool failed or planner declared "cannot_find"
- Use "assertion_failure" if the test expectation is not met (wrong color, missing feature, etc.)
"""

llm = LLM()

def supervisor(state):
    res = state.get("last_action_result") or {}

    # Hard rule: tool/ADB failure => execution_failure
    if not res.get("tool_success", False):
        return {
            "verdict": "fail",
            "failure_type": "execution_failure",
            "notes": res.get("reason", "tool failed"),
            "is_complete": True
        }

    # If planner signaled "cannot_find", that's also execution_failure
    if res.get("action") == "cannot_find":
        return {
            "verdict": "fail",
            "failure_type": "execution_failure",
            "notes": "Required UI element not found",
            "is_complete": True
        }

    # OPTIMIZATION: Skip LLM if UI didn't change (mechanical navigation)
    if not res.get("ui_changed", False) and res.get("tool_success", True):
        # Update no_change_count
        no_change_count = state.get("no_change_count", 0) + 1

        # If too many consecutive no-change steps, fail fast
        # Increased threshold to handle onboarding/modal flows
        if no_change_count >= 5:
            return {
                "verdict": "fail",
                "failure_type": "execution_failure",
                "notes": f"UI did not change after {no_change_count} consecutive attempts",
                "is_complete": True,
                "no_change_count": no_change_count
            }

        return {
            "verdict": "incomplete",
            "is_complete": False,
            "notes": "No UI change detected, continuing exploration",
            "no_change_count": no_change_count
        }

    # Reset no_change_count if UI changed
    no_change_count = 0 if res.get("ui_changed", False) else state.get("no_change_count", 0)

    # If planner signaled "done", evaluate the test outcome
    if res.get("action") == "done":
        # Use vision to verify the test case
        after_path = res.get("after") or state.get("screenshot_path")
        img_bytes = None
        if after_path:
            with open(after_path, "rb") as f:
                img_bytes = f.read()

        prompt = f"""{SUPERVISOR_PROMPT}

TEST CASE:
{state['test_case']}

CURRENT STEP: {state['step']} / {state['max_steps']}

LAST ACTION:
{state.get('last_action')}

EXECUTION RESULT:
{res}

The planner has signaled "done". Verify if the test case is truly satisfied.
Return JSON only."""
        verdict = llm.json(prompt, image_bytes=img_bytes)
        verdict["llm_calls"] = state.get("llm_calls", 0) + 1
        verdict["no_change_count"] = no_change_count
        return verdict

    # Normal case: use vision to evaluate progress
    after_path = res.get("after") or state.get("screenshot_path")
    img_bytes = None
    if after_path:
        with open(after_path, "rb") as f:
            img_bytes = f.read()

    prompt = f"""{SUPERVISOR_PROMPT}

TEST CASE:
{state['test_case']}

CURRENT STEP: {state['step']} / {state['max_steps']}

LAST ACTION:
{state.get('last_action')}

EXECUTION RESULT:
{res}

Evaluate:
1. Is the test case COMPLETE (all requirements met)?
2. If complete, did it PASS or FAIL?
3. If incomplete, return verdict="incomplete" and is_complete=false.

Return JSON only."""
    verdict = llm.json(prompt, image_bytes=img_bytes)
    verdict["llm_calls"] = state.get("llm_calls", 0) + 1
    verdict["no_change_count"] = no_change_count
    return verdict
