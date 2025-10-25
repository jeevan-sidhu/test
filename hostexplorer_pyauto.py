# hostexplorer_pyauto.py
import pyautogui
import pygetwindow as gw
import time
import os
from PIL import Image, ImageChops
from datetime import datetime

# adjust these to taste
DEFAULT_DELAY = 0.08
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
pyautogui.PAUSE = 0.02   # small pause after each PyAutoGUI call

def focus_window(title_substring, raise_if_not_found=True, timeout=5):
    """Activate HostExplorer window by partial title."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        wins = gw.getWindowsWithTitle(title_substring)
        if wins:
            win = wins[0]
            try:
                win.activate()
            except Exception:
                # fallback: try click on center to give focus
                cx, cy = win.left + win.width//2, win.top + win.height//2
                pyautogui.click(cx, cy)
            return win
        time.sleep(0.5)
    if raise_if_not_found:
        raise RuntimeError(f"No window containing '{title_substring}' found.")
    return None

def send_text(text, interval=DEFAULT_DELAY, enter=False):
    pyautogui.typewrite(text, interval=interval)
    if enter:
        pyautogui.press('enter')

def press_pf(n):
    """Press PF keys: 1..12 -> f1..f12 mapping"""
    if 1 <= n <= 12:
        pyautogui.press(f"f{n}")
    else:
        raise ValueError("PF number must be 1-12")

def screenshot_window(win, name_prefix="step"):
    """Take screenshot of the given window (pygetwindow.Window) and save with timestamp."""
    # ensure active
    try:
        win.activate()
    except Exception:
        pass
    left, top, w, h = win.left, win.top, win.width, win.height
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = os.path.join(SCREENSHOT_DIR, f"{name_prefix}_{ts}.png")
    img = pyautogui.screenshot(region=(left, top, w, h))
    img.save(filename)
    return filename

def screenshot_full(name_prefix="full"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = os.path.join(SCREENSHOT_DIR, f"{name_prefix}_{ts}.png")
    img = pyautogui.screenshot()
    img.save(filename)
    return filename

def wait_for_screen_change(win, baseline_image=None, timeout=10, poll=0.5, threshold=10):
    """
    Wait until the window content changes relative to baseline_image (PIL Image) or until timeout.
    Returns the new screenshot filepath. If baseline_image is None, uses current screen as baseline and waits for any change.
    threshold ~ mean pixel difference to consider "changed".
    """
    left, top, w, h = win.left, win.top, win.width, win.height
    def snap():
        return pyautogui.screenshot(region=(left, top, w, h))

    if baseline_image is None:
        baseline_image = snap()

    deadline = time.time() + timeout
    while time.time() < deadline:
        cur = snap()
        diff = ImageChops.difference(baseline_image, cur)
        # calculate a simple metric: bounding box of differences or mean
        bbox = diff.getbbox()
        if bbox is not None:
            # optional: compute average pixel to filter tiny flickers
            stat = sum(diff.convert("L").getextrema())  # quick cheap check
            # if there's any bbox, we treat as changed
            filename = screenshot_window(win, name_prefix="changed")
            return filename
        time.sleep(poll)
    raise TimeoutError("Screen did not change within timeout")
