# xray_manager.py - Xray Core control plane (VLESS-WS ONLY, silent)
import asyncio, json, os, shutil, socket, subprocess, sys, time
from collections import deque
from datetime import datetime
from pathlib import Path


PUBLIC_PORT = int(os.environ.get("PORT", 8080) or 8080)
INTERNAL_PORT = int(os.environ.get("INTERNAL_PORT", 8001) or 8001)
if INTERNAL_PORT == PUBLIC_PORT:
    INTERNAL_PORT = PUBLIC_PORT + 1

WS_PORT = 31801
API_PORT = 20085
os.environ["PORT"] = str(PUBLIC_PORT)
os.environ["INTERNAL_PORT"] = str(INTERNAL_PORT)

_LOG_BUF = deque(maxlen=1000)


def _push(level, msg):
    _LOG_BUF.append((datetime.now().isoformat(timespec="seconds"), level, msg))


def get_logs(limit=300, level=None):
    items = list(_LOG_BUF)[-limit:]
    if level:
        items = [x for x in items if x[1] == level]
    return [{"time": t, "level": lv, "msg": m} for t, lv, m in items]


def clear_logs():
    _LOG_BUF.clear()




# ==================== TOTAL TRAFFIC COUNTER ====================
_TOTAL_BYTES = 0
_TOTAL_BYTES_LOCK = asyncio.Lock()


def get_total_bytes() -> int:
    """Authoritative server-wide total, updated by the stats poller."""
    return _TOTAL_BYTES


def seed_total_from_links() -> int:
    """Recompute the total from per-link used_bytes (call after load_state)."""
    global _TOTAL_BYTES
    try:
        _TOTAL_BYTES = sum(int(l.get("used_bytes", 0) or 0) for l in _links.values())
    except Exception:
        _TOTAL_BYTES = 0
    _log("seeded total_bytes = " + str(_TOTAL_BYTES))
    return _TOTAL_BYTES
BIN_NAME = "xray.exe" if sys.platform.startswith("win") else "xray"
LOCAL_BIN_DIR = Path(__file__).parent / "bin"

XRAY_BIN = None
XRAY_PROC = None
XRAY_VERSION = ""
XHTTP_TRANSPORT = "none"
_process = None
_links = None
_lock = None
_save_state = None
_logger = None
_data_dir = None


def register(links, lock, save_state_fn, logger_obj, data_dir):
    global _links, _lock, _save_state, _logger, _data_dir
    _links = links; _lock = lock; _save_state = save_state_fn
    _logger = logger_obj; _data_dir = Path(data_dir)


def _log(msg, level="info"):
    _push(level, str(msg))


def find_binary():
    global XRAY_BIN
    if XRAY_BIN and XRAY_BIN.exists():
        return XRAY_BIN
    for c in (os.environ.get("XRAY_BIN"), "/usr/local/bin/xray",
              "/usr/bin/xray", str(LOCAL_BIN_DIR / BIN_NAME)):
        if not c:
            continue
        p = Path(c)
        if p.exists():
            XRAY_BIN = p
            return p
    found = shutil.which("xray") or shutil.which("xray.exe")
    if found:
        XRAY_BIN = Path(found)
        return XRAY_BIN
    raise RuntimeError("Xray binary not found")


def ensure_binary():
    return find_binary()


def _detect_version():
    global XRAY_VERSION
    try:
        r = subprocess.run([str(find_binary()), "version"],
                           capture_output=True, text=True, timeout=5)
        out = (r.stdout or "") + (r.stderr or "")
        XRAY_VERSION = out.splitlines()[0] if out else "unknown"
        _log("detected: " + XRAY_VERSION)
    except Exception as e:
        _log("could not detect version: " + str(e), "warning")
        XRAY_VERSION = "unknown"


def _build_config():
    vless = [(uid, l) for uid, l in _links.items() if l.get("active", True)]
    return {
        "log": {"loglevel": "warning"},
        "api": {"tag": "api", "services": ["StatsService", "HandlerService"]},
        "stats": {},
        "policy": {
            "levels": {"0": {"statsUserUplink": True, "statsUserDownlink": True, "connIdle": 300}},
            "system": {"statsInboundUplink": True, "statsInboundDownlink": True},
        },
        "routing": {"rules": [{"type": "field", "inboundTag": ["api"], "outboundTag": "api"}]},
        "inbounds": [
            {"tag": "vless-ws", "listen": "127.0.0.1", "port": WS_PORT,
             "protocol": "vless",
             "settings": {"clients": [{"id": uid, "email": uid, "level": 0, "flow": ""} for uid, _ in vless],
                          "decryption": "none"},
             "streamSettings": {"network": "ws", "wsSettings": {"path": "/ws"}},
             "sniffing": {"enabled": False}},
            {"tag": "api", "listen": "127.0.0.1", "port": API_PORT,
             "protocol": "dokodemo-door", "settings": {"address": "127.0.0.1"}},
        ],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}],
    }


def _write_config():
    cfg = _build_config()
    path = _data_dir / "xray_config.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    tmp.replace(path)
    return path


def _validate_config(cfg_path):
    try:
        r = subprocess.run([str(ensure_binary()), "run", "-c", str(cfg_path), "-test"],
                           capture_output=True, text=True, timeout=10)
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, out.strip()
    except subprocess.TimeoutExpired:
        return False, "xray -test timed out"
    except Exception as e:
        return False, str(e)


def _spawn():
    global XRAY_PROC, _process
    try:
        binary = ensure_binary()
    except RuntimeError as e:
        _log("binary not found: " + str(e), "error")
        return False
    cfg_path = _write_config()
    ok, msg = _validate_config(cfg_path)
    if not ok:
        _log("CONFIG INVALID:\n" + msg, "error")
        return False
    _log("config validated: " + (msg or "ok"))
    for _i in range(20):
        try:
            _s = socket.socket(); _s.settimeout(0.3)
            rc = _s.connect_ex(("127.0.0.1", INTERNAL_PORT)); _s.close()
            if rc == 0:
                break
        except Exception:
            pass
        time.sleep(0.3)
    stdout_log = open(_data_dir / "xray_stdout.log", "ab", buffering=0)
    stdout_log.write(("\n\n=== xray start " + datetime.now().isoformat() + " ===\n").encode())
    stdout_log.flush()
    kwargs = {}
    if sys.platform.startswith("win"):
        kwargs["creationflags"] = 0x08000000
    XRAY_PROC = subprocess.Popen([str(binary), "run", "-c", str(cfg_path)],
                                 stdout=stdout_log, stderr=subprocess.STDOUT, **kwargs)
    _process = XRAY_PROC
    _log("spawned pid=" + str(XRAY_PROC.pid) + " ws=" + str(WS_PORT) +
         " api=" + str(API_PORT))
    time.sleep(1.5)
    if XRAY_PROC.poll() is not None:
        _log("XRAY DIED immediately", "error")
        _dump_logs()
        return False
    _log("xray is alive")
    return True


def _dump_logs():
    for fname in ("xray_stdout.log", "xray_error.log"):
        p = _data_dir / fname
        if not p.exists():
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            _log("--- " + fname + " ---\n" + "\n".join(txt.splitlines()[-60:]), "error")
        except Exception as e:
            _log("could not read " + fname + ": " + str(e), "error")


async def _wait_listen(host, port, timeout=8.0):
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        s = socket.socket(); s.settimeout(0.3)
        try:
            if s.connect_ex((host, port)) == 0:
                return True
        finally:
            s.close()
        await asyncio.sleep(0.3)
    return False


async def start():
    try:
        seed_total_from_links()
    except Exception as _e:
        _log("seed failed: " + str(_e), "warning")
    _detect_version()
    if not _spawn():
        _log("xray failed to start", "error")
        return
    if not await _wait_listen("127.0.0.1", WS_PORT, timeout=8.0):
        _log("WARN: WS port " + str(WS_PORT) + " not listening", "warning")
        _dump_logs()
    else:
        _log("ws port :" + str(WS_PORT) + " is live")
    asyncio.create_task(_config_watcher())


async def stop():
    global XRAY_PROC, _process
    if XRAY_PROC and XRAY_PROC.poll() is None:
        try:
            XRAY_PROC.terminate()
            try:
                XRAY_PROC.wait(timeout=5)
            except subprocess.TimeoutExpired:
                XRAY_PROC.kill(); XRAY_PROC.wait(timeout=2)
        except Exception:
            pass
    XRAY_PROC = None; _process = None
    _log("stopped")


async def reload_config():
    _write_config()
    if not (XRAY_PROC and XRAY_PROC.poll() is None):
        _spawn(); return
    await stop()
    await asyncio.sleep(0.3)
    _spawn()


async def _config_watcher():
    last = None
    while True:
        await asyncio.sleep(5)
        try:
            async with _lock:
                cur = tuple(sorted((u, bool(l.get("active", True))) for u, l in _links.items()))
            if last is None:
                last = cur; continue
            if cur != last:
                _log("Config changed, reloading...")
                last = cur
                await reload_config()
        except Exception as e:
            _log("watcher error: " + str(e), "warning")


async def _api_call(*args):
    proc = await asyncio.create_subprocess_exec(
        str(ensure_binary()), "api", *args,
        "--server", "127.0.0.1:" + str(API_PORT),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(err.decode().strip() or "xray api failed")
    return out.decode()


async def query_stats(reset=True):
    args = ["--reset", "statsquery", "--pattern", "user>>>"] if reset else ["statsquery", "--pattern", "user>>>"]
    try:
        out = await _api_call(*args)
    except Exception:
        return {}
    stats = {}
    try:
        data = json.loads(out)
        for item in data.get("stat", []):
            name = item.get("name", ""); val = int(item.get("value", 0))
            seg = name.split(">>>")
            if len(seg) == 4 and seg[0] == "user" and seg[2] == "traffic":
                stats.setdefault(seg[1], {})[seg[3]] = val
        if stats:
            return stats
    except Exception:
        pass
    for line in out.splitlines():
        line = line.strip().replace('"', "").replace(",", "")
        if ">>>" not in line:
            continue
        parts = line.rsplit(None, 1)
        if len(parts) != 2:
            continue
        try:
            val = int(parts[1])
        except ValueError:
            continue
        seg = parts[0].split(">>>")
        if len(seg) == 4 and seg[0] == "user" and seg[2] == "traffic":
            stats.setdefault(seg[1], {})[seg[3]] = val
    return stats


async def sync_stats_to_links():
    global _TOTAL_BYTES
    if not (XRAY_PROC and XRAY_PROC.poll() is None):
        return
    try:
        deltas = await asyncio.wait_for(query_stats(reset=True), timeout=4.0)
    except Exception as e:
        _log("stats poll failed: " + str(e), "warning")
        return
    if not deltas:
        return

    changed = False
    auto_deactivated = []
    total_delta = 0

    async with _lock:
        for uid, d in deltas.items():
            link = _links.get(uid)
            if not link:
                continue
            delta = int(d.get("uplink", 0)) + int(d.get("downlink", 0))
            if delta <= 0:
                continue
            total_delta += delta
            link["used_bytes"] = link.get("used_bytes", 0) + delta
            link["last_used"] = datetime.now().isoformat()
            changed = True
            lb = link.get("limit_bytes", 0)
            if lb > 0 and link["used_bytes"] >= lb and link.get("active", True):
                link["active"] = False
                auto_deactivated.append(link.get("label", uid))

    if total_delta > 0:
        async with _TOTAL_BYTES_LOCK:
            _TOTAL_BYTES += total_delta
        try:
            import sys as _sys
            _m = _sys.modules.get("main")
            if _m is not None:
                _m.stats["total_bytes"] = _TOTAL_BYTES
                _m.hourly_traffic[datetime.now().strftime("%H:00")] += total_delta
        except Exception:
            pass

    if changed:
        await _save_state()
        if auto_deactivated:
            await reload_config()
            for lbl in auto_deactivated:
                _log("auto-disabled over-quota: " + str(lbl))



def port_status():
    def probe(host, port):
        s = socket.socket(); s.settimeout(0.2)
        try:
            return s.connect_ex((host, port)) == 0
        finally:
            s.close()
    proc = XRAY_PROC
    alive = bool(proc and proc.poll() is None)
    rc = proc.poll() if proc else None
    return {
        "xray_running": alive,
        "xray_pid": proc.pid if proc else None,
        "xray_returncode": rc,
        "xray_version": XRAY_VERSION or "unknown",
        "xhttp_transport": "none",
        "listening": {
            "127.0.0.1:" + str(WS_PORT): probe("127.0.0.1", WS_PORT),
            "127.0.0.1:" + str(API_PORT): probe("127.0.0.1", API_PORT),
        },
    }


def read_log(fname, tail=100):
    p = _data_dir / fname
    if not p.exists():
        return [fname + ": not found"]
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()[-tail:]
    except Exception as e:
        return [fname + ": " + str(e)]


def validate_now():
    try:
        cfg_path = _write_config()
        ok, msg = _validate_config(cfg_path)
        return {"ok": ok, "message": msg, "config_path": str(cfg_path), "xray_version": XRAY_VERSION}
    except Exception as e:
        return {"ok": False, "message": str(e)}


async def diagnose_and_log(delay=1.5):
    await asyncio.sleep(delay)
    st = port_status()
    lines = ["port status:"]
    for k, v in st["listening"].items():
        lines.append("    " + ("OK" if v else "DOWN") + " " + k)
    lines.append("    version=" + str(st["xray_version"]))
    lines.append("    running=" + str(st["xray_running"]) + " pid=" + str(st["xray_pid"]))
    _log("\n".join(lines))
