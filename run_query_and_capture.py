# run_query_and_capture.py
from hostexplorer_pyauto import (
    focus_window, send_text, press_pf, screenshot_window, wait_for_screen_change
)
import time

def main():
    # 1) Focus HostExplorer window (partial title match)
    win = focus_window("HostExplorer", timeout=8)

    # 2) Optional: give yourself a few seconds to confirm focus
    time.sleep(0.5)

    # 3) Baseline screenshot (before sending command)
    base = screenshot_window(win, name_prefix="baseline")

    # 4) Login or navigate (example: send logon command then enter password)
    send_text("LOGON USER01", enter=True)
    time.sleep(1)
    send_text("PASSWORD123", enter=True)

    # 5) Wait for screen change confirming login
    try:
        changed = wait_for_screen_change(win, baseline_image=None, timeout=8)
        print("Screen changed, saved:", changed)
    except TimeoutError:
        print("No screen change detected after login; continuing anyway.")

    # 6) Send SQL (example)
    send_text("RUN SQL", enter=True)
    time.sleep(0.6)   # slight wait for prompt
    send_text('SELECT * FROM MYLIB.MYTABLE WHERE STATUS="A";', enter=True)

    # 7) Wait for result screen to load (using change detection)
    try:
        results_img = wait_for_screen_change(win, baseline_image=None, timeout=12)
        print("Results screen saved:", results_img)
    except TimeoutError:
        # fallback: take screenshot after fixed wait
        time.sleep(2)
        results_img = screenshot_window(win, name_prefix="results_fallback")
        print("Fallback saved:", results_img)

    # 8) Save additional screenshot if you want full-screen
    full = screenshot_window(win, name_prefix="final")
    print("Final screenshot:", full)

if __name__ == "__main__":
    main()
