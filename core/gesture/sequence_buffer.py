from collections import deque
from ..tracker.tracker_fusion import FusedState

class SequenceBuffer:
    def __init__(self, maxlen: int = 30):
        self.buffer = deque(maxlen=maxlen)
        
    def append(self, state: FusedState):
        self.buffer.append(state)
        
    def get_last_n(self, n: int) -> list:
        if len(self.buffer) < n:
            return list(self.buffer)
        return list(self.buffer)[-n:]
        
    def to_tensor(self):
        # Stub for future AI sequence model
        pass
