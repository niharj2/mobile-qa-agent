from graph.workflow import build_graph

TESTS = [
    ("Open Obsidian, create a new Vault named 'InternVault', and enter the vault.", "pass"),
    ("Create a new note titled 'Meeting Notes' and type the text 'Daily Standup' into the body.", "pass"),
    ("Go to Settings and verify that the 'Appearance' tab icon is the color Red.", "fail"),
    ("Find and click the 'Print to PDF' button in the main file menu.", "fail"),
]

if __name__ == "__main__":
    graph = build_graph()

    for t, expected in TESTS:
        state = {
            "test_case": t,
            "plan": None,
            "last_action": None,
            "last_action_result": None,
            "screenshot_path": None,
            "verdict": None,
            "failure_type": None,
            "notes": None,
            "is_complete": None,
            "step": 0,
            "max_steps": 12,
            "llm_calls": 0,  # Track LLM usage
            "no_change_count": 0,  # Track consecutive no-change steps
        }

        print("\n==============================")
        print("TEST:", t)
        print("==============================")

        while state["step"] < state["max_steps"]:
            state["step"] += 1
            state = graph.invoke(state)

            print(f"\n[step {state['step']}] verdict={state.get('verdict')} failure_type={state.get('failure_type')}")
            if state.get("notes"):
                print("notes:", state["notes"])
            if state.get("plan"):
                print("plan:", state["plan"].get("action"), "-", state["plan"].get("why"))

            # Stop only when supervisor says test is complete (is_complete=true)
            # OR when max_steps is reached
            if state.get("is_complete") is True:
                break

        print("\nFINAL:", state.get("verdict"), "| expected:", expected)
        print("failure_type:", state.get("failure_type"))
        print(f"LLM calls: {state.get('llm_calls', 0)} | Steps: {state['step']}")
