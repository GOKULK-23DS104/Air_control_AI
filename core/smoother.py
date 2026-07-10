from __future__ import annotations

import math
import time

Point = tuple[float, float]


class OneEuroFilter1D:
    def __init__(self, t0: float, x0: float, dx0: float = 0.0, min_cutoff: float = 1.0, beta: float = 0.0, d_cutoff: float = 1.0):
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        
        self.x_prev = float(x0)
        self.dx_prev = float(dx0)
        self.t_prev = float(t0)
        
    def __call__(self, t: float, x: float) -> float:
        t_e = t - self.t_prev
        if t_e <= 0.0:
            return self.x_prev # Avoid division by zero
            
        # The filtered derivative of the signal
        a_d = self._alpha(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = self._exponential_smoothing(a_d, dx, self.dx_prev)
        
        # The filtered signal
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._alpha(t_e, cutoff)
        x_hat = self._exponential_smoothing(a, x, self.x_prev)
        
        # Update state
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        
        return x_hat
        
    def _alpha(self, t_e: float, cutoff: float) -> float:
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)
        
    def _exponential_smoothing(self, a: float, x: float, x_prev: float) -> float:
        return a * x + (1 - a) * x_prev


class PointSmoother:
    def __init__(self, min_cutoff: float = 0.5, beta: float = 0.8, d_cutoff: float = 1.0):
        # min_cutoff: Decreasing this reduces jitter but increases lag
        # beta: Increasing this reduces lag but increases jitter at high speeds
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.filter_x: OneEuroFilter1D | None = None
        self.filter_y: OneEuroFilter1D | None = None
        # Keep window_size for backwards compatibility with main.py logging
        self.window_size = "OneEuro Adaptive"
        
    def update(self, point: Point, timestamp: float | None = None) -> Point:
        if timestamp is None:
            timestamp = time.time()
            
        x, y = point
        
        if self.filter_x is None or self.filter_y is None:
            self.filter_x = OneEuroFilter1D(timestamp, x, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
            self.filter_y = OneEuroFilter1D(timestamp, y, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
            return point
            
        return (self.filter_x(timestamp, x), self.filter_y(timestamp, y))
        
    def reset(self) -> None:
        self.filter_x = None
        self.filter_y = None
