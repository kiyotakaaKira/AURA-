import sys

class ContextDetector:
    PROCESS_TO_CONTEXT = {
        "code": "vscode",
        "code.exe": "vscode",
        "chrome": "chrome",
        "chrome.exe": "chrome",
        "firefox": "firefox",
        "firefox.exe": "firefox",
        "spotify": "spotify",
        "spotify.exe": "spotify",
        "explorer.exe": "explorer",
        "finder": "explorer",
        "sublime_text": "sublime",
        "wt.exe": "terminal",
        "terminal": "terminal",
        "iterm2": "terminal",
    }
    
    def get_current_context(self) -> str:
        try:
            if sys.platform == "win32":
                return self._get_context_windows()
            elif sys.platform == "darwin":
                return self._get_context_macos()
            else:
                return "default"
        except Exception:
            return "default"
            
    def _get_context_windows(self) -> str:
        import win32gui
        import win32process
        import psutil
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd: return "default"
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process_name = psutil.Process(pid).name().lower()
            return self.PROCESS_TO_CONTEXT.get(process_name, "default")
        except:
            return "default"
            
    def _get_context_macos(self) -> str:
        import subprocess
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        app_name = result.stdout.strip().lower()
        return self.PROCESS_TO_CONTEXT.get(app_name, "default")
