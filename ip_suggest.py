import random
from pathlib import Path

IPS_FILE = Path(__file__).parent / "ips.txt"

def load_ips() -> list[str]:
    """Read all non‑empty, non‑comment lines from ips.txt."""
    if not IPS_FILE.exists():
        return []
    with open(IPS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def get_random_ips(count: int = 10) -> list[str]:
    """Return a random sample of IP addresses (no duplicates)."""
    all_ips = load_ips()
    if not all_ips:
        return []
    if len(all_ips) <= count:
        return all_ips
    return random.sample(all_ips, count)