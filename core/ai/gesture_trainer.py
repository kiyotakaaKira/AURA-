from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class GestureModelInterface(ABC):
    """
    Standard interface for all gesture models.
    Any model (rule-based, LSTM, TCN, Transformer) must implement this.
    This interface allows model.predict() to be a drop-in replacement.
    """
    
    @abstractmethod
    def predict(self, sequence_buffer) -> Optional[str]:
        """
        Given a sequence buffer, return predicted gesture name or None.
        Must complete in <10ms for real-time use.
        """
        pass
    
    @abstractmethod
    def train(self, gesture_name: str, training_data_path: str) -> dict:
        """Train or fine-tune on new gesture data. Returns training metrics."""
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """Returns confidence of last prediction (0.0-1.0)."""
        pass


class StubGestureModel(GestureModelInterface):
    """
    Placeholder implementation.
    Replace this class with LSTMGestureModel or TCNGestureModel in Phase 2.
    The rest of the codebase only calls GestureModelInterface — zero refactoring needed.
    """
    
    def predict(self, sequence_buffer) -> Optional[str]:
        return None   # Stub: always returns None, gesture_engine falls back to rule-based
    
    def train(self, gesture_name: str, training_data_path: str) -> dict:
        print(f"[STUB] Would train on: {gesture_name}")
        return {"accuracy": 0.0, "loss": 0.0, "status": "stub"}
    
    def get_confidence(self) -> float:
        return 0.0
