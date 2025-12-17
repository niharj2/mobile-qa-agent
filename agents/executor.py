from tools.adb import adb_devices, tap, type_text, keyevent, swipe, launch_app
from tools.screenshot import take_screenshot, images_different
import time

def executor(state):
    if "emulator" not in adb_devices():
        return {
            "last_action_result": {
                "tool_success": False,
                "reason": "No emulator connected",
                "ui_changed": False
            }
        }

    before = take_screenshot("before")

    plan = state["plan"]
    try:
        a = plan["action"]
        if a == "tap":
            tap(plan["x"], plan["y"])
        elif a == "type_text":
            type_text(plan["text"] or "")
        elif a == "keyevent":
            keyevent(plan["keycode"])
        elif a == "swipe":
            s = plan["swipe"]
            swipe(s["x1"], s["y1"], s["x2"], s["y2"], s.get("ms", 300))
        elif a == "launch_app":
            launch_app()
        elif a in ("done", "cannot_find"):
            # These are special actions that don't execute ADB commands
            return {
                "last_action_result": {
                    "tool_success": True,
                    "reason": f"Planner signaled: {a}",
                    "ui_changed": False,
                    "action": a
                },
                "screenshot_path": state.get("screenshot_path")
            }
        else:
            return {
                "last_action_result": {
                    "tool_success": False,
                    "reason": f"Unknown action: {a}",
                    "ui_changed": False
                }
            }
    except Exception as e:
        return {
            "last_action_result": {
                "tool_success": False,
                "reason": f"ADB/tool failure: {e}",
                "ui_changed": False
            }
        }

    # Wait for WebView to render changes after action
    time.sleep(2)

    after = take_screenshot("after")
    changed = images_different(before, after)

    return {
        "last_action_result": {
            "tool_success": True,
            "reason": "Executed",
            "before": before,
            "after": after,
            "ui_changed": changed
        },
        "screenshot_path": after
    }
