from tools.llm import LLM

PLANNER_PROMPT = """You are PLANNER: a mobile QA planning agent for Android apps.
You MUST output ONLY valid JSON.

SCREEN INFO:
- Typical Android phone screen: ~1080x2400 pixels
- Safe tap zone: 100-980 (x), 200-2200 (y)
- Common UI locations:
  * Top bar / menu: y=100-300
  * Bottom nav: y=2000-2300
  * Center content: y=800-1600

Goal: Decide the NEXT SINGLE UI action to complete the test case.

CRITICAL RULES:
1. ONE action at a time.
2. If you are NOT CONFIDENT about exact coordinates, use navigation actions first (menu, scroll, back).
3. Only tap coordinates if you can clearly see a clickable element in the screenshot.
4. If the requested UI element does NOT exist on screen after exploring (menu/scroll/back), declare "cannot_find".
5. Do NOT invent features. If you cannot find "Print to PDF" after 3+ attempts, output "cannot_find".
6. When typing text, make sure a text field is focused first.
7. Use "done" ONLY when ALL test requirements are visually confirmed complete.

RECOVERY POLICY:
- If stuck or unsure: try opening menu (tap hamburger icon or three dots), scroll, or go back
- After 3 failed attempts to find an element: output "cannot_find"

Output schema (strict JSON):
{
  "action": "tap" | "type_text" | "swipe" | "keyevent" | "launch_app" | "done" | "cannot_find",
  "x": int|null,
  "y": int|null,
  "text": str|null,
  "keycode": int|null,
  "swipe": {"x1":int,"y1":int,"x2":int,"y2":int,"ms":int}|null,
  "why": "short reason explaining this specific action"
}

Examples:
- {"action":"tap","x":540,"y":1200,"why":"Tapping 'Create Vault' button"}
- {"action":"type_text","text":"InternVault","why":"Typing vault name"}
- {"action":"swipe","swipe":{"x1":540,"y1":1500,"x2":540,"y2":800,"ms":300},"why":"Scrolling down to find settings"}
- {"action":"cannot_find","why":"Print to PDF button not found after checking menu and scrolling"}
- {"action":"done","why":"Vault 'InternVault' created and entered successfully"}
"""

llm = LLM()

def get_fallback_action(state):
    """Deterministic fallback when UI didn't change"""
    step = state["step"]

    # Cycle through common navigation actions
    fallbacks = [
        {"action": "keyevent", "keycode": 4, "why": "Pressing back to navigate"},
        {"action": "swipe", "swipe": {"x1": 540, "y1": 1500, "x2": 540, "y2": 800, "ms": 300}, "why": "Scrolling down to explore"},
        {"action": "tap", "x": 100, "y": 200, "why": "Tapping top-left menu icon"},
    ]

    return fallbacks[step % len(fallbacks)]

def planner(state):
    from tools.screenshot import take_screenshot

    # OPTIMIZATION 1: Hard cap on total LLM calls
    llm_calls = state.get("llm_calls", 0)
    if llm_calls >= 10:
        return {
            "plan": {"action": "cannot_find", "why": "Exceeded LLM call budget"},
            "last_action": {"action": "cannot_find", "why": "Exceeded LLM call budget"},
            "screenshot_path": state.get("screenshot_path"),
            "llm_calls": llm_calls
        }

    # OPTIMIZATION 2: If last action had no UI change, use fallback immediately
    last_result = state.get("last_action_result", {})

    # Key optimization: Don't call LLM if UI didn't change in previous step
    if last_result and not last_result.get("ui_changed", True):
        fallback = get_fallback_action(state)
        no_change_count = state.get("no_change_count", 0)
        print(f"[PLANNER] Using fallback (UI unchanged): {fallback['action']}")
        return {
            "plan": fallback,
            "last_action": fallback,
            "screenshot_path": state.get("screenshot_path"),
            "llm_calls": llm_calls,  # Don't increment
            "no_change_count": no_change_count
        }

    # Normal path: use LLM
    screenshot_path = state.get("screenshot_path")

    # Take a screenshot if we don't have one yet
    if not screenshot_path:
        screenshot_path = take_screenshot(f"step_{state['step']}")

    img_bytes = None
    if screenshot_path:
        with open(screenshot_path, "rb") as f:
            img_bytes = f.read()

    prompt = f"""{PLANNER_PROMPT}

TEST CASE:
{state['test_case']}

CURRENT STEP: {state['step']} / {state['max_steps']}

PREVIOUS ACTION (if any):
{state.get('last_action')}

LAST EXECUTION RESULT (if any):
{state.get('last_action_result')}

Analyze the screenshot and decide the NEXT action.
Be conservative with coordinates. If unsure, explore first.
Return JSON only."""

    plan = llm.json(prompt, image_bytes=img_bytes)

    print(f"[PLANNER] LLM decision: {plan['action']}")

    return {
        "plan": plan,
        "last_action": plan,
        "screenshot_path": screenshot_path,
        "llm_calls": llm_calls + 1  # Increment LLM counter
    }
