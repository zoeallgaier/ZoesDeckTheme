"""Press keys in a Gaming Mode window: zdt_key.py SP ArrowRight [ArrowRight ...]"""
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("cef", "tools/cef.py")
cef = importlib.util.module_from_spec(spec); spec.loader.exec_module(cef)
dt = cef.DevTools(cef.pick_tab(sys.argv[1])["webSocketDebuggerUrl"])
codes = {"ArrowRight": 39, "ArrowLeft": 37, "ArrowUp": 38, "ArrowDown": 40, "Enter": 13, "Escape": 27}
for key in sys.argv[2:]:
    for t in ("rawKeyDown", "keyUp"):
        dt.call("Input.dispatchKeyEvent", type=t, key=key, code=key, windowsVirtualKeyCode=codes[key], nativeVirtualKeyCode=codes[key])
    time.sleep(0.4)
