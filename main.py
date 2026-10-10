# main.py — MX-UI v1.0.0 (Xray Core data plane)
import asyncio
import json
import os
import hashlib
import secrets
import time
import aiofiles
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote, parse_qs
from collections import deque, defaultdict
from pathlib import Path
import random
import socket
from concurrent.futures import ThreadPoolExecutor
import sys
import psutil
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import Response, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import logging
import re

from qr_generator import generate_qr_base64
from pages import SETUP_HTML, LOGIN_HTML, DASHBOARD_HTML, SUB_USER_HTML, SUB_INFO_HTML, LOGS_HTML
from ip_suggest import get_random_ips

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MX-UI")

IRAN_TZ = ZoneInfo("Asia/Tehran")

async def _prune_connections_loop():
    while True:
        await asyncio.sleep(120)
        try:
            now = time.time()
            stale = []
            for cid, c in list(connections.items()):
                ca = c.get("connected_at")
                if not ca:
                    continue
                try:
                    from datetime import datetime as _dt
                    age = (datetime.now() - _dt.fromisoformat(ca)).total_seconds()
                except Exception:
                    continue
                if age > 7200:
                    stale.append(cid)
            for cid in stale:
                connections.pop(cid, None)
            if stale:
                logger.info(f"[prune] removed {len(stale)} stale connections")
        except Exception as e:
            logger.debug(f"[prune] {e}")

@asynccontextmanager
async def _lifespan(app_instance: FastAPI):
    global http_client
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    http_client = httpx.AsyncClient(limits=limits, timeout=timeout, follow_redirects=True)
    await load_state()


    _xray_ok = False
    _xray_last_err = None
    for _attempt in range(3):
        try:
            await xray_manager.start()
            await xray_manager.diagnose_and_log()
            _st = xray_manager.port_status()
            _listen = _st.get("listening", {}) or {}
            ws_port = getattr(xray_manager, "WS_PORT", 31801)
            
            # Check ONLY for the WS_PORT to declare Xray running
            if _listen.get(f"127.0.0.1:{ws_port}"):
                _xray_ok = True
                break
                
            _xray_last_err = "xray WS port not listening"
            logger.warning(f"[xray] attempt {_attempt + 1}/3: {_xray_last_err}")
        except Exception as e:
            _xray_last_err = f"{type(e).__name__}: {e}"
            logger.error(f"[xray] attempt {_attempt + 1}/3 failed: {_xray_last_err}")
        await asyncio.sleep(2)

    if not _xray_ok:
        logger.error("[xray] CRITICAL: failed to start after 3 attempts")
        log_activity("system", f"Xray failed: {_xray_last_err}", "err")

    asyncio.create_task(_xray_stats_loop())
    asyncio.create_task(_prune_connections_loop())
    log_activity("system", "Server started (VLESS-WS Only)", "ok")
    yield

    await save_state()
    try:
        await xray_manager.stop()
    except Exception as e:
        logger.warning(f"[xray] stop failed: {e}")
    if http_client:
        await http_client.aclose()



    await save_state()
    try:
        await xray_manager.stop()
    except Exception as e:
        logger.warning(f"[xray] stop failed: {e}")
    if http_client:
        await http_client.aclose()



    await save_state()
    try:
        await xray_manager.stop()
    except Exception as e:
        logger.warning(f"[xray] stop failed: {e}")
    if http_client:
        await http_client.aclose()

app = FastAPI(title="MX-UI", docs_url=None, redoc_url=None, lifespan=_lifespan)

DECORATIVE_EMOJIS = ["🌸", "🌺", "🌻", "🌹", "🌷", "🌿", "🍀", "🌴", "🌳", "🎋",
                     "💎", "🌟", "✨", "🎯", "🏆", "🔥", "💨", "🚀", "⭐", "💫",
                     "🌈", "⚡", "🎉", "🎊", "💝", "🌊", "🍃"]

IP_CACHE = {}
IP_CACHE_LOCK = asyncio.Lock()
IP_CACHE_TTL = 3600

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_FILE = DATA_DIR / "mxui_state.json"
SECRET_FILE = DATA_DIR / "mxui_secret.key"
SETUP_COMPLETE_FILE = DATA_DIR / "setup_complete.lock"
SAVE_LOCK = asyncio.Lock()

def _load_or_create_secret() -> str:
    env_secret = os.environ.get("SECRET_KEY")
    if env_secret:
        return env_secret
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if SECRET_FILE.exists():
            existing = SECRET_FILE.read_text(encoding="utf-8").strip()
            if existing:
                return existing
        new_secret = secrets.token_urlsafe(32)
        SECRET_FILE.write_text(new_secret, encoding="utf-8")
        return new_secret
    except Exception as e:
        logger.warning(f"Could not persist SECRET_KEY: {e}")
        return secrets.token_urlsafe(32)

CONFIG = {
    "port": int(os.environ.get("PORT", 8080)),
    "secret": _load_or_create_secret(),
    "host": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost"),
    "dashboard_path": "/dashboard",
    "login_path": "/login",
    "sub_path": "/sub",
    "setup_path": "/setup",
}

PUBLIC_PORT = int(os.environ.get("PORT", 8080) or 8080)
INTERNAL_PORT = int(os.environ.get("INTERNAL_PORT", 8001) or 8001)
if INTERNAL_PORT == PUBLIC_PORT:
    INTERNAL_PORT = PUBLIC_PORT + 1
    os.environ["INTERNAL_PORT"] = str(INTERNAL_PORT)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: dict = {}
stats = {
    "total_bytes": 0,
    "total_requests": 0,
    "total_errors": 0,
    "start_time": time.time(),
}
error_logs: deque = deque(maxlen=50)
activity_logs: deque = deque(maxlen=200)
hourly_traffic: dict = defaultdict(int)
http_client: httpx.AsyncClient | None = None
LINKS: dict = {}
LINKS_LOCK = asyncio.Lock()

PROTOCOLS = ("vless-ws",)
DEFAULT_PROTOCOL = "vless-ws"

PROTOCOL_ALIASES = {}

PROTOCOL_FAMILIES = ("vless",)
TRANSPORTS = ("ws",)
XHTTP_MODES = ()

def parse_protocol(proto: str) -> tuple[str, str, str]:
    """WS-only: always returns (vless, ws, "")."""
    return "vless", "ws", ""


def build_protocol(family: str, transport: str, mode: str = "") -> str:
    """WS-only: always returns 'vless-ws'."""
    return "vless-ws"


FINGERPRINTS = ("chrome", "firefox", "safari", "ios", "android", "edge", "360", "qq", "random", "randomized")
DEFAULT_FINGERPRINT = "chrome"
DEFAULT_ALPN_BY_PROTOCOL = {"vless-ws": "http/1.1"}
DEFAULT_PORT = 443
DEFAULT_SPEED_LIMIT = 0

async def load_state():
    global LINKS, AUTH, CONFIG
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = await f.read()
            data = json.loads(raw)
            LINKS.update(data.get("links", {}))
            for uid, link in LINKS.items():
                if "ip_pool" not in link:
                    link["ip_pool"] = []
            if "password_hash" in data:
                AUTH["password_hash"] = data["password_hash"]
            if "paths" in data:
                for key, value in data["paths"].items():
                    if key in CONFIG:
                        CONFIG[key] = value
            logger.info(f"State loaded: {len(LINKS)} links")
    except Exception as e:
        logger.warning(f"Could not load state: {e}")

async def save_state():
    async with SAVE_LOCK:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "links": dict(LINKS),
                "password_hash": AUTH["password_hash"],
                "saved_at": datetime.now().isoformat(),
                "paths": {
                    "dashboard_path": CONFIG.get("dashboard_path", "/dashboard"),
                    "login_path": CONFIG.get("login_path", "/login"),
                    "sub_path": CONFIG.get("sub_path", "/sub"),
                    "setup_path": CONFIG.get("setup_path", "/setup"),
                },
            }
            tmp = DATA_FILE.with_suffix(".tmp")
            async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            tmp.replace(DATA_FILE)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")

def log_activity(kind: str, message: str, level: str = "info"):
    activity_logs.append({
        "kind": kind,
        "level": level,
        "message": message,
        "time": datetime.now().isoformat(),
    })

SESSION_COOKIE = "mxui_session"
SESSION_TTL = 60 * 60 * 24 * 365

def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{pw}{CONFIG['secret']}".encode()).hexdigest()

AUTH = {"password_hash": hash_password(os.environ.get("ADMIN_PASSWORD", "MUVIXO"))}
SESSIONS: dict = {}
SESSIONS_LOCK = asyncio.Lock()

async def create_session() -> str:
    token = secrets.token_urlsafe(32)
    async with SESSIONS_LOCK:
        SESSIONS[token] = time.time() + SESSION_TTL
    return token

async def is_valid_session(token: str | None) -> bool:
    if not token:
        return False
    async with SESSIONS_LOCK:
        exp = SESSIONS.get(token)
        if exp is None:
            return False
        if exp < time.time():
            SESSIONS.pop(token, None)
            return False
        return True

async def destroy_session(token: str | None):
    if not token:
        return
    async with SESSIONS_LOCK:
        SESSIONS.pop(token, None)

async def clear_all_sessions():
    async with SESSIONS_LOCK:
        SESSIONS.clear()

async def require_auth(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not await is_valid_session(token):
        raise HTTPException(status_code=401, detail="unauthorized")
    return token

def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"

def client_ip(request: Request) -> str:
    return get_client_ip(request)

def now_ir() -> datetime:
    return datetime.now(IRAN_TZ)

def uptime() -> str:
    secs = int(time.time() - stats["start_time"])
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_host(request: Optional[Request] = None) -> str:
    if request is not None:
        h = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if h:
            return h.split(":")[0]
    return os.environ.get("RAILWAY_PUBLIC_DOMAIN", CONFIG["host"])

def generate_uuid() -> str:
    h = secrets.token_hex(16)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

def fmt_bytes(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    if b < 1024 ** 2:
        return f"{b/1024:.1f} KB"
    if b < 1024 ** 3:
        return f"{b/1024**2:.2f} MB"
    return f"{b/1024**3:.2f} GB"

def fmt_bytes_short(b: int) -> str:
    return fmt_bytes(b)

def parse_size_to_bytes(value: float, unit: str) -> int:
    unit = unit.upper()
    if unit == "GB":
        return int(value * 1024 ** 3)
    if unit == "MB":
        return int(value * 1024 ** 2)
    if unit == "KB":
        return int(value * 1024)
    return int(value)

def parse_speed_to_bytes(value: float, unit: str) -> int:
    if value <= 0:
        return 0
    unit = (unit or "MBIT").upper()
    if unit == "MBIT":
        return int(value * 1024 * 1024 / 8)
    if unit == "KB":
        return int(value * 1024)
    if unit == "MB":
        return int(value * 1024 * 1024)
    return int(value)

def is_link_expired(link: dict) -> bool:
    exp = link.get("expires_at")
    if not exp:
        return False
    try:
        return datetime.now() > datetime.fromisoformat(exp)
    except Exception:
        return False

def is_link_allowed(link: dict | None) -> bool:
    if link is None:
        return False
    if not link.get("active", True):
        return False
    if is_link_expired(link):
        return False
    lb = link.get("limit_bytes", 0)
    if lb > 0 and link.get("used_bytes", 0) >= lb:
        return False
    return True

def unique_ips_for_uuid(uuid: str) -> set:
    return {c.get("ip") for c in connections.values() if c.get("uuid") == uuid and c.get("ip")}

def get_random_decorative_emoji() -> str:
    return random.choice(DECORATIVE_EMOJIS)

def format_limit(limit_bytes: int) -> tuple[str, str]:
    if limit_bytes == 0:
        return "♾️", "∞"
    if limit_bytes >= 1024 ** 3:
        gb = limit_bytes / 1024 ** 3
        display = f"{gb:.0f} GB" if gb >= 100 else f"{gb:.1f} GB"
        emoji = "📦" if gb < 10 else ("🚀" if gb < 100 else "🌌")
        return emoji, display
    if limit_bytes >= 1024 ** 2:
        return "📦", f"{limit_bytes / 1024**2:.0f} MB"
    return "📦", f"{limit_bytes / 1024:.0f} KB"

def generate_emoji_label(base_label: str, limit_bytes: int, speed_limit_bytes: int) -> str:
    clean_label = re.sub(r'[^a-zA-Z\s\-\.]', '', base_label).strip() or "Config"
    random_emoji = get_random_decorative_emoji()
    limit_emoji, limit_display = format_limit(limit_bytes)
    speed_emoji = "⚡" if speed_limit_bytes > 0 else "🐢"
    return f"{random_emoji} {clean_label} {limit_emoji} {limit_display} {speed_emoji}"

def is_setup_complete() -> bool:
    try:
        if SETUP_COMPLETE_FILE.exists():
            return True
        return AUTH["password_hash"] != hash_password("MUVIXO")
    except Exception:
        return False

async def mark_setup_complete():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETUP_COMPLETE_FILE.write_text("setup_complete", encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not mark setup complete: {e}")

def generate_vless_link(
    uuid: str, host: str, remark: str = "MX-UI", protocol: str = "vless-ws",
    fingerprint: str | None = None, alpn: str | None = None,
    connect_address: str | None = None, connect_port: int | None = None,
    password: str | None = None,
) -> str:
    fp = (fingerprint or "chrome").strip()
    alpn_val = (alpn or "http/1.1").strip()
    port_val = connect_port or 443
    address = connect_address or host

    params = {
        "security": "tls", "type": "ws", "host": host, "path": "/ws",
        "sni": host, "fp": fp, "alpn": alpn_val, "encryption": "none"
    }
    query = "&".join(f"{k}={quote(str(v), safe=',/:')}" for k, v in params.items())
    return f"vless://{uuid}@{address}:{port_val}?{query}#{quote(remark)}"

def vless_link_for_link(link: dict, uid: str, host: str) -> str:
    proto = link.get("protocol", DEFAULT_PROTOCOL)
    family, _, _ = parse_protocol(proto)
    return generate_vless_link(
        uid, host,
        remark=f"MX-UI-{link.get('label','')}",
        protocol=proto,
        fingerprint=link.get("fingerprint"),
        alpn=link.get("alpn"),
        password=uid if family == "trojan" else None,
    )

def build_all_vless_links(link: dict, uid: str, host: str) -> list[str]:
    proto = link.get("protocol", DEFAULT_PROTOCOL)
    fp = link.get("fingerprint")
    alpn = link.get("alpn")
    base_remark = f"MX-UI-{link.get('label','')}"

    out = [generate_vless_link(
        uid, host, remark=f"{base_remark} (Domain)",
        protocol=proto, fingerprint=fp, alpn=alpn
    )]
    for i, entry in enumerate(link.get("ip_pool") or [], start=1):
        ip = entry.get("ip")
        port = entry.get("port") or DEFAULT_PORT
        if ip:
            out.append(generate_vless_link(
                uid, host, remark=f"{base_remark} (IP {i})",
                protocol=proto, fingerprint=fp, alpn=alpn,
                connect_address=ip, connect_port=port
            ))
    return out

import xray_manager

WS_PORT = getattr(xray_manager, "WS_PORT", 31801)

xray_manager.register(LINKS, LINKS_LOCK, save_state, logger, DATA_DIR)

async def _xray_stats_loop():
    while True:
        await asyncio.sleep(5)
        try:
            await xray_manager.sync_stats_to_links()
            stats["total_bytes"] = xray_manager.get_total_bytes()
        except Exception as e:
            logger.debug(f"[xray-stats] {e}")



async def ensure_default_link():
    global _default_link_created
    if _default_link_created:
        return
    async with LINKS_LOCK:
        if not any(l.get("is_default") for l in LINKS.values()):
            uid = hashlib.sha256(f"default{CONFIG['secret']}".encode()).hexdigest()
            uid = f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:32]}"
            if uid not in LINKS:
                LINKS[uid] = {
                    "label": "♾️ Default Link ∞ 🐢",
                    "limit_bytes": 0,
                    "used_bytes": 0,
                    "created_at": datetime.now().isoformat(),
                    "active": True,
                    "expires_at": None,
                    "note": "",
                    "is_default": True,
                    "protocol": DEFAULT_PROTOCOL,
                    "fingerprint": DEFAULT_FINGERPRINT,
                    "alpn": "",
                    "ip_limit": 0,
                    "speed_limit_bytes": DEFAULT_SPEED_LIMIT,
                    "last_used": None,
                    "country": "Default",
                    "ip_pool": [],
                }
                asyncio.create_task(save_state())
        _default_link_created = True

# ===== HEALTH & SYSTEM DIAGNOSTICS =====
@app.get("/healthz")
@app.get("/health")
async def healthz():
    xray_ok = False
    try:
        st = xray_manager.port_status()
        xray_ok = bool(st.get("xray_running"))
    except Exception:
        pass
    return {"ok": True, "service": "mx-ui", "xray_running": xray_ok, "uptime": uptime()}

@app.get("/readyz")
async def readyz():
    try:
        st = xray_manager.port_status()
        if st.get("xray_running"):
            return {"ready": True}
    except Exception:
        pass
    raise HTTPException(status_code=503, detail="not ready")

# ===== WEB PAGES & AUTH RENDERING =====
@app.get("/")
async def root(request: Request):
    dashboard_path = CONFIG.get("dashboard_path", "/dashboard")
    if dashboard_path == "/":
        return await render_dashboard(request)
    return RedirectResponse(url=dashboard_path, status_code=302)

@app.get("/dashboard")
async def dashboard_default(request: Request):
    dashboard_path = CONFIG.get("dashboard_path", "/dashboard")
    if dashboard_path != "/dashboard":
        return RedirectResponse(url=dashboard_path, status_code=302)
    return await render_dashboard(request)

@app.get("/login")
async def login_default(request: Request):
    login_path = CONFIG.get("login_path", "/login")
    if login_path != "/login":
        return RedirectResponse(url=login_path, status_code=302)
    return await render_login(request)

@app.get("/setup")
async def setup_page(request: Request):
    if is_setup_complete():
        login_path = CONFIG.get("login_path", "/login")
        return RedirectResponse(url=login_path, status_code=302)
    return HTMLResponse(content=SETUP_HTML)

async def render_dashboard(request: Request):
    if not is_setup_complete():
        setup_path = CONFIG.get("setup_path", "/setup")
        return RedirectResponse(url=setup_path, status_code=302)
    token = request.cookies.get(SESSION_COOKIE)
    valid = await is_valid_session(token)
    if not valid:
        login_path = CONFIG.get("login_path", "/login")
        return RedirectResponse(url=login_path, status_code=302)
    await ensure_default_link()
    return HTMLResponse(content=DASHBOARD_HTML)

async def render_login(request: Request):
    if not is_setup_complete():
        setup_path = CONFIG.get("setup_path", "/setup")
        return RedirectResponse(url=setup_path, status_code=302)
    if await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        dashboard_path = CONFIG.get("dashboard_path", "/dashboard")
        return RedirectResponse(url=dashboard_path, status_code=302)
    return HTMLResponse(content=LOGIN_HTML)

# ===== SUBSCRIPTION PAGES =====
def render_sub_user_html(**kwargs) -> str:
    html = SUB_USER_HTML
    for key, value in kwargs.items():
        html = html.replace(f"%%{key.upper()}%%", str(value))
    return html

async def subscription_user_handler(request: Request, uuid: str):
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    if not link:
        raise HTTPException(status_code=404, detail="not found")

    host = get_host(request)
    vless = vless_link_for_link(link, uuid, host)
    used = link.get("used_bytes", 0)
    limit = link.get("limit_bytes", 0)

    if limit > 0 and used >= limit and link.get("active", True):
        async with LINKS_LOCK:
            LINKS[uuid]["active"] = False
        await save_state()
        async with LINKS_LOCK:
            link = LINKS.get(uuid)

    active = is_link_allowed(link)
    expiry = link.get("expires_at", "No expiry")
    last_online = link.get("last_used", "Never")
    ips = unique_ips_for_uuid(uuid)
    ip_display = ", ".join(ips) if ips else "No active connections"
    ips_count = len(ips)

    status_text = "Active" if active else "Inactive"
    status_color = "text-emerald-400" if active else "text-red-400"
    status_dot = "active" if active else "inactive"
    status_html = f'<span class="status-dot {status_dot}"></span><span class="{status_color} font-semibold">{status_text}</span>'

    quota_str = "∞" if limit == 0 else fmt_bytes(limit)
    remained = "∞" if limit == 0 else fmt_bytes(max(0, limit - used))
    usage_pct = 0 if limit == 0 else min(100, (used / limit) * 100)

    qr_base64 = generate_qr_base64(vless, size=300)
    all_links = build_all_vless_links(link, uuid, host)
    links_rows = []
    for i, l in enumerate(all_links):
        tag = "Domain" if i == 0 else f"IP {i}"
        tag_class = "domain" if i == 0 else "ip"
        safe_l = l.replace("'", "&#39;").replace('"', "&quot;")
        links_rows.append(
            f'<div class="link-row flex items-center gap-2 border-b border-slate-800/40 py-2 px-1 hover:bg-slate-800/20 transition-colors">'
            f'<span class="link-tag {tag_class}">{tag}</span>'
            f'<input type="text" readonly value="{safe_l}" class="flex-1 min-w-0 bg-slate-950 border border-slate-800/80 rounded-lg px-2 py-1 text-[9px] font-mono text-slate-400 select-all truncate">'
            f'<button onclick="navigator.clipboard.writeText(\'{safe_l}\')" class="px-2 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs">Copy</button>'
            f'</div>'
        )
    links_list_html = "".join(links_rows) if links_rows else '<p class="text-xs text-slate-500 p-3">No links available</p>'

    return HTMLResponse(content=render_sub_user_html(
        label=link.get("label", "Unknown"),
        uuid=uuid,
        qr_url=qr_base64,
        status=status_html,
        status_color=status_color,
        status_dot=status_dot,
        status_text=status_text,
        downloaded=fmt_bytes(used),
        uploaded="0 B",
        usage=fmt_bytes(used),
        total_quota=quota_str,
        remained=remained,
        last_online=last_online,
        expiry=expiry,
        ips=ip_display,
        ips_count=ips_count,
        usage_pct=round(usage_pct, 1),
        used_fmt=fmt_bytes(used),
        limit_fmt=quota_str,
        links_list_html=links_list_html,
        applied_ips_count=len(link.get("ip_pool") or []),
        watermark="Created by Muvixo",
        vless_link=vless,
    ))

@app.get("/sub/user")
async def subscription_user_old(request: Request, uuid: str = Query(...)):
    return await subscription_user_handler(request, uuid)

@app.get("/sub/{uuid}")
async def subscription_single(uuid: str, request: Request):
    import base64
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    if not link or not is_link_allowed(link):
        raise HTTPException(status_code=404, detail="not found or inactive")
    host = get_host(request)
    all_links = build_all_vless_links(link, uuid, host)
    content = base64.b64encode("\n".join(all_links).encode()).decode()
    return Response(content=content, media_type="text/plain")

@app.get("/sub-all")
async def subscription_all(request: Request, _=Depends(require_auth)):
    import base64
    host = get_host(request)
    async with LINKS_LOCK:
        lines = []
        for uid, d in LINKS.items():
            if is_link_allowed(d):
                lines.extend(build_all_vless_links(d, uid, host))
    content = base64.b64encode("\n".join(lines).encode()).decode()
    return Response(content=content, media_type="text/plain")

# ===== API ROUTES =====
@app.post("/api/setup")
async def setup_admin(request: Request):
    body = await request.json()
    password = str(body.get("password", ""))
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    AUTH["password_hash"] = hash_password(password)
    await mark_setup_complete()
    await clear_all_sessions()
    await save_state()
    return {"ok": True, "message": "Password set successfully"}

@app.post("/api/login")
async def api_login(request: Request):
    if not is_setup_complete():
        raise HTTPException(status_code=403, detail="Setup required. Please visit /setup")
    body = await request.json()
    if hash_password(str(body.get("password", ""))) != AUTH["password_hash"]:
        raise HTTPException(status_code=401, detail="Wrong password")
    token = await create_session()
    resp = JSONResponse({"ok": True})
    resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_TTL, httponly=True, samesite="lax", path="/")
    return resp

@app.post("/api/logout")
async def api_logout(request: Request):
    await destroy_session(request.cookies.get(SESSION_COOKIE))
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp

@app.get("/api/me")
async def api_me(request: Request):
    return {"authenticated": await is_valid_session(request.cookies.get(SESSION_COOKIE))}

@app.get("/api/is-default-password")
async def is_default_password():
    return {"is_default": AUTH["password_hash"] == hash_password("MUVIXO")}

@app.get("/api/current-paths")
async def get_current_paths():
    return {
        "dashboard": CONFIG.get("dashboard_path", "/dashboard"),
        "login": CONFIG.get("login_path", "/login"),
        "sub": CONFIG.get("sub_path", "/sub"),
        "setup": CONFIG.get("setup_path", "/setup"),
    }

@app.get("/api/get-paths")
async def get_paths(_=Depends(require_auth)):
    return {
        "dashboard_path": CONFIG.get("dashboard_path", "/dashboard"),
        "login_path": CONFIG.get("login_path", "/login"),
        "sub_path": CONFIG.get("sub_path", "/sub"),
        "setup_path": CONFIG.get("setup_path", "/setup"),
    }

@app.post("/api/change-password")
async def api_change_password(request: Request, token=Depends(require_auth)):
    body = await request.json()
    if hash_password(str(body.get("current_password", ""))) != AUTH["password_hash"]:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    new = str(body.get("new_password", ""))
    if len(new) < 4:
        raise HTTPException(status_code=400, detail="New password must be at least 4 characters")
    AUTH["password_hash"] = hash_password(new)
    await mark_setup_complete()
    await clear_all_sessions()
    await save_state()
    return {"ok": True, "requires_login": True}

@app.get("/stats")
async def get_stats(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count(logical=True)
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    try:
        disk = psutil.disk_usage('/')
    except Exception:
        disk = psutil.disk_usage('.')

    return {
        "active_connections": len(connections),
        "total_traffic_mb": round(xray_manager.get_total_bytes() / (1024 ** 2), 2),
        "total_requests": stats["total_requests"],
        "total_errors": stats["total_errors"],
        "uptime": uptime(),
        "timestamp": datetime.now().isoformat(),
        "hourly": dict(hourly_traffic),
        "recent_errors": list(error_logs)[-10:],
        "links_count": len(snap),
        "active_links": sum(1 for l in snap.values() if is_link_allowed(l)),
        "expired_links": sum(1 for l in snap.values() if is_link_expired(l)),
        "cpu_percent": round(cpu_percent, 1),
        "cpu_cores": cpu_count,
        "ram_used_mb": ram.used // (1024 * 1024),
        "ram_total_mb": ram.total // (1024 * 1024),
        "ram_percent": ram.percent,
        "swap_used_mb": swap.used // (1024 * 1024),
        "swap_total_mb": swap.total // (1024 * 1024),
        "swap_percent": swap.percent,
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_percent": disk.percent,
    }

@app.get("/api/links")
async def list_links(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    async with LINKS_LOCK:
        snap = dict(LINKS)
    result = []
    for uid, d in snap.items():
        result.append({
            "uuid": uid,
            **d,
            "expired": is_link_expired(d),
            "vless_link": vless_link_for_link(d, uid, host),
            "sub_url": f"https://{host}/sub/{uid}",
            "info_url": f"https://{host}/sub/{uid}/info",
            "connected_ips": len(unique_ips_for_uuid(uid)),
            "is_default": d.get("is_default", False),
            "applied_ips_count": len(d.get("ip_pool") or []),
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"links": result}

@app.post("/api/links")
async def create_link(request: Request, _=Depends(require_auth)):
    body = await request.json()
    lv = float(body.get("limit_value") or 0)
    lu = body.get("limit_unit") or "GB"
    limit_bytes = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
    exp_days = int(body.get("expires_days") or 0)
    expires_at = (datetime.now() + timedelta(days=exp_days)).isoformat() if exp_days > 0 else None
    try:
        ip_limit = int(body.get("ip_limit") or 0)
    except Exception:
        ip_limit = 0

    sv = float(body.get("speed_limit_value") or 0)
    su = body.get("speed_limit_unit") or "MBIT"
    speed_limit_bytes = 0 if sv <= 0 else parse_speed_to_bytes(sv, su)

    protocol = body.get("protocol") or DEFAULT_PROTOCOL
    fp = body.get("fingerprint") or DEFAULT_FINGERPRINT
    uid = generate_uuid()
    formatted_label = generate_emoji_label(body.get("label") or "Config", limit_bytes, speed_limit_bytes)

    async with LINKS_LOCK:
        LINKS[uid] = {
            "label": formatted_label,
            "limit_bytes": max(0, limit_bytes),
            "used_bytes": 0,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "expires_at": expires_at,
            "note": (body.get("note") or "").strip()[:200],
            "is_default": False,
            "protocol": protocol,
            "fingerprint": fp,
            "alpn": (body.get("alpn") or "").strip()[:100],
            "ip_limit": max(0, ip_limit),
            "speed_limit_bytes": max(0, speed_limit_bytes),
            "last_used": None,
            "country": "Unknown",
            "ip_pool": [],
        }
    asyncio.create_task(save_state())
    host = get_host(request)
    return {
        "uuid": uid,
        **LINKS[uid],
        "expired": False,
        "vless_link": vless_link_for_link(LINKS[uid], uid, host),
        "sub_url": f"https://{host}/sub/{uid}",
    }

@app.patch("/api/links/{uid}")
async def update_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        link = LINKS[uid]
        if link.get("is_default", False):
            raise HTTPException(status_code=403, detail="Default configuration cannot be modified")
        if "active" in body:
            link["active"] = bool(body["active"])
        if "label" in body:
            link["label"] = str(body["label"])
        if "protocol" in body:
            link["protocol"] = str(body["protocol"])
        if "fingerprint" in body:
            link["fingerprint"] = str(body["fingerprint"])
        if "alpn" in body:
            link["alpn"] = str(body["alpn"])
    asyncio.create_task(save_state())
    return {"ok": True}

@app.delete("/api/links/{uid}")
async def delete_link(uid: str, _=Depends(require_auth)):
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        if LINKS[uid].get("is_default", False):
            raise HTTPException(status_code=403, detail="Default configuration cannot be deleted")
        del LINKS[uid]
    asyncio.create_task(save_state())
    return {"ok": True}

@app.patch("/api/links/{uid}/toggle")
async def toggle_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    active = bool(body.get("active", True))
    async with LINKS_LOCK:
        if uid in LINKS:
            LINKS[uid]["active"] = active
    asyncio.create_task(save_state())
    return {"ok": True, "active": active}

@app.post("/api/links/{uid}/reset-traffic")
async def reset_traffic(uid: str, _=Depends(require_auth)):
    async with LINKS_LOCK:
        if uid in LINKS:
            LINKS[uid]["used_bytes"] = 0
            LINKS[uid]["active"] = True
    asyncio.create_task(save_state())
    return {"ok": True}

@app.get("/api/qr")
async def get_qr(request: Request):
    data = request.query_params.get("data", "")
    if not data:
        raise HTTPException(status_code=400, detail="Missing data")
    return {"qr": generate_qr_base64(data, size=300)}

@app.get("/api/domain/check")
async def check_domain(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    return {"host": host, "is_railway": "railway.app" in host}

@app.get("/api/ips/suggest")
async def suggest_ips(_=Depends(require_auth)):
    ips = get_random_ips(10)
    return {"ips": ips, "count": len(ips)}

@app.post("/api/ips/apply")
async def apply_ips(request: Request, _=Depends(require_auth)):
    body = await request.json()
    new_ips = body.get("ips", [])
    target_uuids = body.get("target_uuids", [])
    async with LINKS_LOCK:
        for uid in target_uuids:
            if uid in LINKS:
                LINKS[uid]["ip_pool"] = [{"ip": ip, "port": 443} for ip in new_ips]
    await save_state()
    return {"ok": True}

@app.get("/api/database/export")
async def export_db(_=Depends(require_auth)):
    async with LINKS_LOCK:
        return {"links": dict(LINKS), "exported_at": datetime.now().isoformat()}



# ===== DYNAMIC ROUTE CATCH-ALL (MUST BE AFTER SPECIFIC ROUTES) =====



# ==================== LOGS PAGE ====================
@app.get("/logs")
async def logs_page(request: Request):
    if not is_setup_complete():
        return RedirectResponse(url=CONFIG.get("setup_path", "/setup"), status_code=302)
    if not await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url=CONFIG.get("login_path", "/login"), status_code=302)
    return HTMLResponse(content=LOGS_HTML)


@app.get("/api/logs")
async def api_logs(_=Depends(require_auth), limit: int = 300, level: str = None):
    try:
        return {"logs": xray_manager.get_logs(limit=limit, level=level)}
    except Exception as e:
        return {"logs": [], "error": str(e)}


@app.post("/api/logs/clear")
async def api_logs_clear(_=Depends(require_auth)):
    try:
        xray_manager.clear_logs(); return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs/ports")
async def api_logs_ports(_=Depends(require_auth)):
    try:
        return xray_manager.port_status()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/logs/files/{name}")
async def api_logs_files(name: str, _=Depends(require_auth), tail: int = 200):
    if name not in ("xray_stdout.log", "xray_error.log"):
        raise HTTPException(status_code=404, detail="not found")
    return {"lines": xray_manager.read_log(name, tail=tail)}


@app.get("/{path:path}")
async def dynamic_catchall(request: Request, path: str):
    if path in ("ws",) or path.startswith("ws/"):
        return Response(status_code=404)
    if path.startswith("api/") or path.startswith("stats") or path.startswith("health"):
        raise HTTPException(status_code=404, detail="Not Found")

    dashboard_path = CONFIG.get("dashboard_path", "/dashboard").lstrip("/")
    login_path = CONFIG.get("login_path", "/login").lstrip("/")
    setup_path = CONFIG.get("setup_path", "/setup").lstrip("/")
    sub_path = CONFIG.get("sub_path", "/sub").lstrip("/")

    if path == dashboard_path or path == "dashboard":
        return await render_dashboard(request)
    if path == login_path or path == "login":
        return await render_login(request)
    if path == setup_path or path == "setup":
        return await setup_page(request)
    if path.startswith(sub_path):
        sub_uuid = path[len(sub_path):].strip("/")
        if sub_uuid:
            return await subscription_single(sub_uuid, request)
    return RedirectResponse(url=f"/{dashboard_path}", status_code=302)

# ===================== ALL VPN PROTOCOL PROXIES =====================


# ==================== HEALTH TEST ENDPOINT (Fix 405) ====================


# ==================== HEALTH TEST ENDPOINT ====================


# ==================== HEALTH TEST ENDPOINT ====================
_executor = ThreadPoolExecutor(max_workers=20)

def _tcp_test_node(host: str, port: int, timeout: float = 3.0):
    try:
        t0 = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            return (time.time() - t0) * 1000
    except Exception:
        return None

@app.post("/api/configs/test")
async def test_configs(request: Request, _=Depends(require_auth)):
    body = await request.json()
    uuids = body.get("uuids", [])
    if not uuids:
        raise HTTPException(status_code=400, detail="No UUIDs provided")

    host = get_host(request)
    async with LINKS_LOCK:
        snap = {uid: dict(LINKS.get(uid) or {}) for uid in uuids}

    loop = asyncio.get_event_loop()
    results = {}

    for uid in uuids:
        link = snap.get(uid)
        if not link:
            results[uid] = {"healthy": False, "latency": None, "error": "Not found"}
            continue

        targets = []
        for entry in (link.get("ip_pool") or []):
            ip = entry.get("ip")
            port = entry.get("port") or DEFAULT_PORT
            if ip:
                targets.append((ip, port))
        if host and host not in ("localhost", "127.0.0.1"):
            targets.append((host, DEFAULT_PORT))

        if not targets:
            results[uid] = {"healthy": False, "latency": None, "error": "No targets"}
            continue

        healthy = False
        latency = None
        for thost, tport in targets:
            ms = await loop.run_in_executor(_executor, _tcp_test_node, thost, tport, 3.0)
            if ms is not None:
                healthy = True
                latency = ms
                break

        results[uid] = {
            "healthy": healthy,
            "latency": latency,
            "error": None if healthy else "Unreachable"
        }

    return {"results": results}


# ==================== WEBSOCKET PROXY (VLESS-WS ONLY) ====================
@app.websocket("/ws")
async def ws_vless_proxy(websocket: WebSocket):
    import websockets as _ws
    await websocket.accept()
    ws_port = getattr(xray_manager, "WS_PORT", 31801)
    target_url = f"ws://127.0.0.1:{ws_port}/ws"

    try:
        xray_ws = await _ws.connect(
            target_url,
            max_size=None,
            ping_interval=20,
            ping_timeout=20,
            open_timeout=10,
            close_timeout=5,
        )
    except Exception as e:
        logger.warning(f"[ws-proxy] backend connection failed: {e}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
        return

    stop_event = asyncio.Event()

    async def c2x():
        try:
            while not stop_event.is_set():
                msg = await websocket.receive()
                if msg.get("type") == "websocket.disconnect":
                    break
                data = msg.get("bytes") or (msg.get("text") or "").encode()
                if data:
                    await xray_ws.send(data)
        except Exception:
            pass
        finally:
            stop_event.set()

    async def x2c():
        try:
            async for m in xray_ws:
                if stop_event.is_set():
                    break
                if isinstance(m, bytes):
                    await websocket.send_bytes(m)
                else:
                    await websocket.send_text(m)
        except Exception:
            pass
        finally:
            stop_event.set()

    t1 = asyncio.create_task(c2x())
    t2 = asyncio.create_task(x2c())

    # Wait until one direction encounters a true closure
    await stop_event.wait()

    for t in (t1, t2):
        if not t.done():
            t.cancel()

    try:
        if not xray_ws.closed:
            await xray_ws.close()
    except Exception:
        pass
    try:
        await websocket.close()
    except Exception:
        pass



if __name__ == "__main__":
    _public = int(os.environ.get("PORT", 8080) or 8080)
    _internal = int(os.environ.get("INTERNAL_PORT", 8001) or 8001)
    os.environ["PUBLIC_PORT"] = str(_public)
    os.environ["INTERNAL_PORT"] = str(_internal)
    uvicorn.run("main:app", host="0.0.0.0", port=_public, log_level="warning", workers=1)
