import pytest
import numpy as np
from core.smoothing.one_euro_filter import OneEuroFilter, OneEuroFilter2D
from core.smoothing.kalman_filter import KalmanFilter2D
from core.smoothing.dead_zone import DeadZoneFilter

def test_one_euro_reduces_noise():
    """Filter should reduce RMS noise on a noisy constant-position signal."""
    f = OneEuroFilter(min_cutoff=1.0, beta=0.007)
    
    # Generate noisy constant signal: true position = 0.5, noise ±0.05
    np.random.seed(42)
    noisy = [0.5 + np.random.normal(0, 0.05) for _ in range(100)]
    
    filtered = [f.filter(v, t * 0.033) for t, v in enumerate(noisy)]
    
    raw_rms = np.sqrt(np.mean([(v - 0.5)**2 for v in noisy]))
    filtered_rms = np.sqrt(np.mean([(v - 0.5)**2 for v in filtered[20:]]))   # Skip warmup
    
    assert filtered_rms < raw_rms * 0.5, "Filter should reduce noise by at least 50%"

def test_one_euro_tracks_fast_movement():
    """Filter should track fast movement without excessive lag."""
    f = OneEuroFilter(min_cutoff=1.0, beta=0.007)
    
    # Ramp from 0.0 to 1.0 over 30 frames
    inputs = [i / 30.0 for i in range(30)]
    outputs = [f.filter(v, i * 0.033) for i, v in enumerate(inputs)]
    
    # At frame 30, output should be within 20% of true position
    assert abs(outputs[-1] - 1.0) < 0.2, "Should track fast movement within 20%"

def test_dead_zone_suppresses_micro_movement():
    f = DeadZoneFilter(threshold_px=3.0)
    
    pos1 = f.filter((100.0, 100.0))
    pos2 = f.filter((101.0, 100.5))   # < 3px movement
    
    assert pos1 == pos2, "Movement < threshold should be suppressed"

def test_dead_zone_passes_large_movement():
    f = DeadZoneFilter(threshold_px=3.0)
    
    pos1 = f.filter((100.0, 100.0))
    pos2 = f.filter((110.0, 100.0))   # > 3px movement
    
    assert pos1 != pos2, "Movement > threshold should pass through"
