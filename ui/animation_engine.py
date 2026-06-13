import time
import math

class Spring:
    def __init__(self, stiffness=200, damping=20, mass=1.0):
        self.stiffness = stiffness
        self.damping = damping
        self.mass = mass
        self.value = 0.0
        self.target = 0.0
        self.velocity = 0.0
        self.last_time = time.time()

    def update(self):
        now = time.time()
        dt = min(now - self.last_time, 0.1)
        self.last_time = now
        
        force = -self.stiffness * (self.value - self.target) - self.damping * self.velocity
        acceleration = force / self.mass
        self.velocity += acceleration * dt
        self.value += self.velocity * dt
        return self.value

class AnimationEngine:
    def __init__(self):
        self.springs = {}

    def get_pulse(self, period_ms: int) -> float:
        """Returns a sine wave value between 0.0 and 1.0."""
        t = time.time()
        return (math.sin(t * 2 * math.pi / (period_ms / 1000.0)) + 1) / 2
        
    def get_spring(self, name: str, target: float) -> float:
        if name not in self.springs:
            self.springs[name] = Spring()
            self.springs[name].value = target
            self.springs[name].target = target
            
        spring = self.springs[name]
        spring.target = target
        return spring.update()
