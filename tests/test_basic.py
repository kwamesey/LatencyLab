from latency_lab.utils import compute_jitter

def test_jitter():
    assert compute_jitter([]) == 0.0
