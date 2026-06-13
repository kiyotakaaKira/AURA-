import winsound
import threading
import time

class AudioFeedback:
    @staticmethod
    def play_tick():
        # Play a very short, high pitch click
        threading.Thread(target=lambda: winsound.Beep(2500, 10), daemon=True).start()

    @staticmethod
    def play_activate():
        # Ascending short tone
        def sound():
            winsound.Beep(800, 50)
            winsound.Beep(1200, 50)
        threading.Thread(target=sound, daemon=True).start()

    @staticmethod
    def play_deactivate():
        # Descending short tone
        def sound():
            winsound.Beep(1200, 50)
            winsound.Beep(800, 50)
        threading.Thread(target=sound, daemon=True).start()

    @staticmethod
    def play_dismiss_step():
        threading.Thread(target=lambda: winsound.Beep(600, 100), daemon=True).start()

    @staticmethod
    def play_dismiss_cancel():
        def sound():
            winsound.Beep(400, 150)
            winsound.Beep(300, 250)
        threading.Thread(target=sound, daemon=True).start()

    @staticmethod
    def play_shutdown():
        def sound():
            winsound.Beep(1500, 150)
            time.sleep(0.05)
            winsound.Beep(1000, 200)
            time.sleep(0.05)
            winsound.Beep(500, 400)
        threading.Thread(target=sound, daemon=True).start()

    @staticmethod
    def play_startup():
        def sound():
            winsound.Beep(800, 150)
            time.sleep(0.05)
            winsound.Beep(1200, 200)
            time.sleep(0.05)
            winsound.Beep(1800, 400)
        threading.Thread(target=sound, daemon=True).start()
