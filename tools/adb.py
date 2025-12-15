import subprocess, os

ADB_PATH = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")

def adb_devices():
    r = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, check=True)
    return r.stdout

def tap(x, y): subprocess.run([ADB_PATH, "shell", "input", "tap", str(x), str(y)], check=True)
def type_text(s): subprocess.run([ADB_PATH, "shell", "input", "text", s.replace(" ", "%s")], check=True)
def keyevent(code): subprocess.run([ADB_PATH, "shell", "input", "keyevent", str(code)], check=True)
def swipe(x1,y1,x2,y2,ms=300): subprocess.run([ADB_PATH,"shell","input","swipe",str(x1),str(y1),str(x2),str(y2),str(ms)], check=True)
def launch_app(pkg="md.obsidian"): subprocess.run([ADB_PATH,"shell","monkey","-p",pkg,"-c","android.intent.category.LAUNCHER","1"], check=True)
