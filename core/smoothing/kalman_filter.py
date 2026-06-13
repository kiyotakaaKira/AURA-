import numpy as np

class CursorKalmanFilter:
    """
    2D Kalman filter for cursor position.
    
    State vector: [x, y, vx, vy]
    - x, y: position in screen pixels
    - vx, vy: velocity in pixels/frame
    """
    
    def __init__(self, process_noise: float = 0.01, measurement_noise: float = 0.1):
        self.pn = process_noise
        self.mn = measurement_noise
        
        # State: [x, y, vx, vy]
        self.x = np.zeros((4, 1))
        
        # State transition matrix (constant velocity model)
        self.F = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=float)
        
        # Measurement matrix (we only measure position, not velocity)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=float)
        
        # Process noise covariance
        self.Q = np.eye(4) * process_noise
        
        # Measurement noise covariance
        self.R = np.eye(2) * measurement_noise
        
        # Error covariance matrix
        self.P = np.eye(4) * 1.0
        
        self._initialized = False
    
    def update(self, measured_x: float, measured_y: float) -> tuple:
        measurement = np.array([[measured_x], [measured_y]])
        
        if not self._initialized:
            self.x[0, 0] = measured_x
            self.x[1, 0] = measured_y
            self._initialized = True
            return (measured_x, measured_y)
        
        # Predict step
        x_pred = self.F @ self.x
        P_pred = self.F @ self.P @ self.F.T + self.Q
        
        # Update step
        S = self.H @ P_pred @ self.H.T + self.R
        K = P_pred @ self.H.T @ np.linalg.inv(S)
        
        self.x = x_pred + K @ (measurement - self.H @ x_pred)
        self.P = (np.eye(4) - K @ self.H) @ P_pred
        
        return (float(self.x[0, 0]), float(self.x[1, 0]))
    
    def reset(self, x: float = 0, y: float = 0):
        """Call when tracking is lost. Prevents stale velocity from causing a jump."""
        self.x = np.array([[x], [y], [0.0], [0.0]])
        self.P = np.eye(4) * 1.0
        self._initialized = False
