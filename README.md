# Mobile QA Multi-Agent System

A LangGraph-based multi-agent system for automated mobile QA testing of Android applications using Gemini vision models.

## Architecture

The system implements a **Supervisor-Planner-Executor** pattern:

- **Planner**: Analyzes screenshots using Gemini vision to decide the next UI action
- **Executor**: Executes planned actions via ADB commands (tap, type, swipe, etc.)
- **Supervisor**: Verifies test outcomes and distinguishes between execution failures and assertion failures

## Project Structure

```
mobile_qa_agent/
├── agents/
│   ├── planner.py
│   ├── executor.py
│   └── supervisor.py
├── tools/
│   ├── adb.py
│   ├── screenshot.py
│   └── llm.py
├── graph/
│   ├── state.py
│   └── workflow.py
├── screenshots/
├── logs/
├── main.py
├── config.py
└── report.md

```

## Prerequisites

### 1. Android SDK Setup

Install Android Studio and set up the Android SDK:

```bash
# Verify ADB is available
~/Library/Android/sdk/platform-tools/adb --version
```

### 2. Android Emulator

Create an AVD (Android Virtual Device):

1. Open Android Studio � AVD Manager
2. Create a device (e.g., Pixel 6, API Level 34+)
3. Use a system image with Google Play APIs

Start the emulator:

```bash
EMULATOR_NAME=your_avd_name
~/Library/Android/sdk/emulator/emulator -avd $EMULATOR_NAME -no-snapshot
```

### 3. Install Obsidian App

Download and install Obsidian for Android:

```bash
# Install APK on emulator
~/Library/Android/sdk/platform-tools/adb install path/to/obsidian.apk

# Verify installation
~/Library/Android/sdk/platform-tools/adb shell pm list packages | grep obsidian
```

## Installation

### 1. Clone the repository

```bash
cd mobile_qa_agent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

## Usage

### Run all test cases

```bash
python main.py
```

This will execute the following test scenarios against the Obsidian app:

1. Create a new Vault named 'InternVault'
2. Create a note titled 'Meeting Notes'
3. Verify UI appearance attributes (expected assertion failure)
4. Attempt to locate 'Print to PDF' (expected execution failure)

Each test demonstrates a different outcome category (pass, assertion failure, execution failure).

### Output

The system will:
- Take screenshots at each step
- Print agent decisions and actions
- Report final verdict (pass/fail) and failure type
- Save screenshots to `screenshots/` directory

Example output:

```
==============================
TEST: Find and click the 'Print to PDF' button
==============================

[step 1] verdict=None failure_type=None
[PLANNER] {'action': 'tap', 'x': 500, 'y': 200, 'why': 'Opening menu'}

[step 2] verdict=fail failure_type=execution_failure
notes: UI element not found after 3 attempts

FINAL: fail | expected: fail
failure_type: execution_failure
```

## Test Cases

All test cases are defined in `main.py`:

```python
TESTS = [
    ("Open Obsidian, create a new Vault named 'InternVault', and enter the vault.", "pass"),
    ("Create a new note titled 'Meeting Notes' and type the text 'Daily Standup' into the body.", "pass"),
    ("Go to Settings and verify that the 'Appearance' tab icon is the color Red.", "fail"),
    ("Find and click the 'Print to PDF' button in the main file menu.", "fail"),
]
```

## Configuration

Edit `config.py` to customize:

- `GEMINI_MODEL`: Change Gemini model (default: `gemini-1.5-flash`)
- `MAX_STEPS`: Maximum steps per test (default: 12)
- `OBSIDIAN_PACKAGE`: Android package name
- `ADB_PATH`: Path to ADB binary

## Architecture Details

### State Flow

```
Planner → Executor → Supervisor
   ↑                        ↓
   └───────── shared state ─┘
```

### Failure Classification

- **Execution Failure**: Tool/ADB failures, UI element not found when needed
- **Assertion Failure**: Steps succeeded but expected condition is false

This distinction helps QA teams understand whether a bug is in the test automation or the app itself.

### Performance Optimizations

The system implements several optimizations to reduce LLM API costs and improve execution speed:

**1. UI Change Gating**
- Supervisor skips LLM calls when UI didn't change (`ui_changed=False`)
- Reduces redundant API calls for mechanical navigation steps
- Automatically fails after 3 consecutive no-change steps

**2. Fallback Navigation**
- When UI doesn't change for 2+ steps, Planner uses deterministic fallback actions (back, scroll, menu)
- Avoids LLM calls for simple navigation recovery
- Cycles through common navigation patterns

**3. Hard Cap on LLM Calls**
- Maximum 10 LLM calls per test to prevent runaway costs
- Automatically signals `cannot_find` when budget exceeded
- Demonstrates cost-awareness in agent design

**4. Intelligent Retry Budget**
- Tracks consecutive steps with no UI change
- Fast-fails tests that are clearly stuck
- Prevents infinite exploration loops

**Impact:** These optimizations significantly reduce redundant LLM calls while maintaining test accuracy.

## Dependencies

- `langgraph` - Multi-agent orchestration
- `google-generativeai` - Gemini API client
- `pillow` - Image processing for screenshots
- `python-dotenv` - Environment variable management

## Troubleshooting

### "No emulator connected"

Ensure the emulator is running:

```bash
~/Library/Android/sdk/platform-tools/adb devices
```

You should see output like:

```
List of devices attached
emulator-5554   device
```

### "GEMINI_API_KEY not found"

Make sure:
1. `.env` file exists in the project root
2. Contains `GEMINI_API_KEY=your_key`
3. No quotes around the key

### Screenshots not saving

Check permissions:

```bash
mkdir -p screenshots logs
chmod 755 screenshots logs
```

## Future Enhancements

- Add retry logic for flaky UI elements
- Implement parallel test execution
- Add HTML test report generation
- Support for iOS testing via Appium
- Integration with CI/CD pipelines

## License

MIT

## Author

QualGent Research Intern Coding Challenge - December 2025