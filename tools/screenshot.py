from PIL import Image, ImageChops
import subprocess
import time
import os

ADB_PATH = os.path.expanduser(
    "~/Library/Android/sdk/platform-tools/adb"
)

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(prefix="screen"):
    timestamp = int(time.time())
    device_path = f"/sdcard/{prefix}_{timestamp}.png"
    local_path = f"{SCREENSHOT_DIR}/{prefix}_{timestamp}.png"

    # 1. Take screenshot ON DEVICE
    subprocess.run(
        [ADB_PATH, "shell", "screencap", "-p", device_path],
        check=True
    )

    # 2. Pull it to host
    subprocess.run(
        [ADB_PATH, "pull", device_path, local_path],
        check=True
    )

    # 3. Cleanup device file (optional but clean)
    subprocess.run(
        [ADB_PATH, "shell", "rm", device_path],
        check=True
    )

    return local_path

def images_different(img1_path, img2_path) -> bool:
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")

    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is not None
