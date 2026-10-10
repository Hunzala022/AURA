import time
import random
import datetime

# Milestone 3.3: Human-like interaction and Rate limits

class RateLimiter:
    def __init__(self, max_actions_per_hour: int = 20):
        self.max_actions = max_actions_per_hour
        self.action_timestamps = []

    def check_limit(self) -> bool:
        """Returns True if action is allowed, False if rate limited."""
        now = datetime.datetime.now()
        # Remove timestamps older than 1 hour
        self.action_timestamps = [
            t for t in self.action_timestamps
            if isinstance(t, datetime.datetime) and (now - t).total_seconds() < 3600
        ]
        
        if len(self.action_timestamps) >= self.max_actions:
            return False
        
        self.action_timestamps.append(now)
        return True

# Global rate limiter for communication tasks
COMM_RATE_LIMITER = RateLimiter(max_actions_per_hour=30)

def human_typing(target_control, text: str):
    """
    Simulates human typing with random delays between keystrokes.
    target_control: A uiautomation EditControl or DocumentControl.
    """
    target_control.Click()
    
    # Random pause before typing
    time.sleep(random.uniform(0.5, 1.5))
    
    for char in text:
        target_control.SendKeys(char)
        # Random typing delay (fast typist: 50-150ms)
        time.sleep(random.uniform(0.05, 0.15))
        
        # 5% chance of a micro-pause (simulating thinking/reading)
        if random.random() < 0.05:
            time.sleep(random.uniform(0.3, 0.8))

def human_delay():
    """Generic random delay between UI actions."""
    time.sleep(random.uniform(0.8, 2.5))
