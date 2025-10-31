from __future__ import annotations
import asyncio, platform, statistics, time, subprocess, shlex
from typing import List, Dict, Any

def now_ms() -> int:
    return int(time.time() * 1000)

def compute_jitter(samples_ms: List[float]) -> float:
    if len(samples_ms) < 2:
        return 0.0
    return statistics.pstdev(samples_ms)

async def ping_once(host: str, timeout: int = 2) -> float | None:
    # Cross-platform ping (using OS ping). Returns latency in ms or None if timeout/failure.
    system = platform.system().lower()
    if system == 'windows':
        cmd = f'ping -n 1 -w {timeout*1000} {shlex.quote(host)}'
    else:
        cmd = f'ping -c 1 -W {timeout} {shlex.quote(host)}'
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout + 1)
        text = stdout.decode(errors='ignore')
        for token in text.split():
            if token.startswith('time=') and token.endswith('ms'):
                try:
                    return float(token.split('=',1)[1].replace('ms','').strip())
                except ValueError:
                    pass
        if 'time<' in text and 'ms' in text:
            return 0.5
    except asyncio.TimeoutError:
        return None
    except Exception:
        return None
    return None

async def probe_targets(targets: List[str], timeout: int = 2) -> Dict[str, float | None]:
    results: Dict[str, float | None] = {}
    coros = [ping_once(t, timeout=timeout) for t in targets]
    latencies = await asyncio.gather(*coros, return_exceptions=True)
    for t, val in zip(targets, latencies):
        if isinstance(val, Exception):
            results[t] = None
        else:
            results[t] = val
    return results
