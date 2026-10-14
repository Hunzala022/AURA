import time
import random
import datetime
import sqlite3
import hashlib
from pathlib import Path
from contextlib import closing

# Milestone 3.3: Human-like interaction and Rate limits

class RateLimiter:
    def __init__(self, max_actions_per_hour: int = 20):
        self.max_actions = max_actions_per_hour
        self.action_timestamps = []

    def check_limit(self, platform='default') -> bool:
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
class PersistentRateLimiter:
    """Atomic reservation, rolling 24h per exact application and global hour cap.

    Attempts consume quota even on uncertain delivery; never retry a send blindly.
    A storage failure denies sending. No recipients or message bodies are stored.
    """
    def __init__(self,path=None,hourly=30,daily=100,clock=time.time,global_daily=100):
        self.path=Path(path or Path(__file__).resolve().parent.parent/'.aura-private/communication_limits.db')
        self.hourly=hourly;self.daily=daily;self.clock=clock;self.global_daily=global_daily

    def check_limit(self,platform='default'):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with closing(sqlite3.connect(self.path,timeout=10)) as db, db:
                db.execute('CREATE TABLE IF NOT EXISTS attempts (platform TEXT, timestamp REAL)')
                db.execute('BEGIN IMMEDIATE')
                now=self.clock()
                # Backward clock changes fail closed until time catches up.
                last=db.execute('SELECT MAX(timestamp) FROM attempts').fetchone()[0]
                if last is not None and now<last:return False
                name=hashlib.sha256(platform.strip().casefold().encode()).hexdigest()
                hour=db.execute('SELECT COUNT(*) FROM attempts WHERE timestamp>?',(now-3600,)).fetchone()[0]
                day=db.execute('SELECT COUNT(*) FROM attempts WHERE platform=? AND timestamp>?',(name,now-86400)).fetchone()[0]
                total=db.execute('SELECT COUNT(*) FROM attempts WHERE timestamp>?',(now-86400,)).fetchone()[0]
                if hour>=self.hourly or day>=self.daily or total>=self.global_daily:return False
                db.execute('DELETE FROM attempts WHERE timestamp<=?',(now-86400,))
                db.execute('INSERT INTO attempts VALUES (?,?)',(name,now))
                return True
        except (OSError,sqlite3.Error):return False

def _production_limiter():
    from core.storage_selection import encrypted_paths
    paths=encrypted_paths()
    if paths is None:return PersistentRateLimiter()
    from core.encrypted_limits import EncryptedRateLimiter
    return EncryptedRateLimiter(paths['quota'],paths['key'])

COMM_RATE_LIMITER = _production_limiter()

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

def cursor_curve(start,end,steps=18,rng=random):
    """Bounded quadratic path, including exact endpoints; no clicking."""
    import math
    if steps<2:raise ValueError('At least two cursor samples required')
    dx=end[0]-start[0];dy=end[1]-start[1];length=math.hypot(dx,dy)
    if not length:return [tuple(end)]
    bend=min(40.,length*.15)*rng.choice((-1,1))
    middle=((start[0]+end[0])/2-dy/length*bend,(start[1]+end[1])/2+dx/length*bend)
    return [(round((1-t)**2*start[0]+2*(1-t)*t*middle[0]+t*t*end[0]),
             round((1-t)**2*start[1]+2*(1-t)*t*middle[1]+t*t*end[1]))
            for t in (i/(steps-1) for i in range(steps))]

def move_pointer_to(auto,control):
    """Move only to an observed, nonempty control rectangle; never click."""
    try:
        rect=control.BoundingRectangle
        if not all(isinstance(v,(int,float)) for v in (rect.left,rect.top,rect.right,rect.bottom)) or rect.right<=rect.left or rect.bottom<=rect.top:return False
        target=(round((rect.left+rect.right)/2),round((rect.top+rect.bottom)/2))
        for point in cursor_curve(auto.GetCursorPos(),target):
            auto.SetCursorPos(*point);time.sleep(random.uniform(.008,.025))
        return auto.GetCursorPos()==target
    except (AttributeError,TypeError,ValueError,OSError):return False

def typing_pause():
    time.sleep(random.uniform(.05,.15))
