import sys
import math
from ..smoothing.exponential_smoother import ExponentialSmoother

class VolumeController:
    def __init__(self, config: dict):
        self.enabled = config.get('volume', {}).get('enabled', True)
        self.smoothing_alpha = config.get('volume', {}).get('smoothing_alpha', 0.15)
        self.smoother = ExponentialSmoother(alpha=self.smoothing_alpha)
        
        self.platform = sys.platform
        self._audio_interface = None
        self._volume_obj = None
        
        if self.enabled:
            self._init_backend()
            
    def _init_backend(self):
        if self.platform == "win32":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self._volume_obj = cast(interface, POINTER(IAudioEndpointVolume))
            except Exception as e:
                print(f"  [AURA] [WARN] Volume controller: {e}")
                self.enabled = False
        else:
            # macOS and Linux stub
            pass
            
    def update(self, thumb_tip: tuple, index_tip: tuple, palm_width: float):
        if not self.enabled:
            return
            
        dx = thumb_tip[0] - index_tip[0]
        dy = thumb_tip[1] - index_tip[1]
        raw_distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalize distance based on palm width to make it hand-size invariant
        normalized_distance = raw_distance / (palm_width + 1e-5)
        
        # Map normalized distance (approx 0.5 to 2.5) to 0.0 - 1.0
        min_dist = 0.5
        max_dist = 2.0
        
        vol_ratio = (normalized_distance - min_dist) / (max_dist - min_dist)
        vol_ratio = max(0.0, min(1.0, vol_ratio))
        
        smoothed_vol = self.smoother.filter(vol_ratio)
        
        self._set_volume(smoothed_vol)
        
    def _set_volume(self, ratio: float):
        if self.platform == "win32" and self._volume_obj:
            # pycaw uses scalar 0.0 to 1.0
            try:
                self._volume_obj.SetMasterVolumeLevelScalar(ratio, None)
            except:
                pass
        elif self.platform == "darwin":
            # macOS via osascript
            import subprocess
            vol = int(ratio * 100)
            subprocess.run(['osascript', '-e', f'set volume output volume {vol}'], capture_output=True)
