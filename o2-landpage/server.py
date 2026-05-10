#!/usr/bin/env python3
"""
server.py v2 — O2 Data Solutions
FastAPI + WAF + Rate Limit + IP Ban + Hot Reload + Rich Console
Visitors DB + Queues + Async + Cookie Consent + Security Headers

pip install fastapi uvicorn pyyaml pandas numpy colorama rich watchdog aiofiles
"""
# ── stdlib ────────────────────────────────────────────────────────────────────
import os, sys, re, json, sqlite3, smtplib, ssl, logging, time, datetime, uuid
import hashlib, threading, asyncio, queue, collections, ipaddress
from pathlib import Path
from logging.handlers import RotatingFileHandler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

# ── third-party ───────────────────────────────────────────────────────────────
try:
    import yaml
    import pandas as pd
    import numpy as np
    from fastapi import FastAPI, Request, HTTPException, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
    from pydantic import BaseModel
    import uvicorn
    try:
        import colorama
        from colorama import Fore, Back, Style
        colorama.init(autoreset=True)
        HAS_COLOR = True
    except ImportError:
        HAS_COLOR = False
        class Fore:
            GREEN=CYAN=YELLOW=RED=MAGENTA=BLUE=WHITE=LIGHTBLUE_EX=LIGHTGREEN_EX=LIGHTYELLOW_EX=LIGHTRED_EX=LIGHTMAGENTA_EX=RESET=""
        class Style:
            BRIGHT=DIM=RESET_ALL=""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.live import Live
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.text import Text
        from rich.columns import Columns
        HAS_RICH = True
        rich_console = Console()
    except ImportError:
        HAS_RICH = False
        rich_console = None
except ImportError as e:
    print(f"\n[ERRO] Dependencia faltando: {e}")
    print("pip install fastapi uvicorn pyyaml pandas numpy colorama rich watchdog aiofiles\n")
    sys.exit(1)


# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
LOG_DIR  = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
CFG_DIR  = BASE_DIR / "config"
DB_PATH       = DATA_DIR / "o2_metrics.db"
VISITORS_DB   = DATA_DIR / "visitors.db"
BANS_DB       = DATA_DIR / "bans.db"

for d in [LOG_DIR, DATA_DIR]:
    d.mkdir(exist_ok=True)

# ── YAML loader ───────────────────────────────────────────────────────────────
def load_yaml(name: str) -> dict:
    p = CFG_DIR / name
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

APP_CFG  = load_yaml("app.yaml")
EMAIL_CFG= load_yaml("email.yaml")
SRV_CFG  = load_yaml("server.yaml")
SEC_CFG  = load_yaml("security.yaml")
VIS_CFG  = load_yaml("visitors.yaml")
PERF_CFG = load_yaml("performance.yaml")
CONS_CFG = load_yaml("consent.yaml")

# ── Config shortcuts ──────────────────────────────────────────────────────────
PORT         = SRV_CFG.get("server", {}).get("port", 80)
SMTP_HOST    = EMAIL_CFG.get("smtp", {}).get("host",     "smtp-relay.brevo.com")
SMTP_PORT    = EMAIL_CFG.get("smtp", {}).get("port",     465)
SMTP_USER    = EMAIL_CFG.get("smtp", {}).get("username", "chaos4455@gmail.com")
SMTP_PASS    = EMAIL_CFG.get("smtp", {}).get("password", "pZz9rCt2I5SdjKsY")
SENDER_EMAIL = EMAIL_CFG.get("sender", {}).get("email", "contato@o2data.com.br")
SENDER_NAME  = EMAIL_CFG.get("sender", {}).get("name",  "O2 Data Solutions")
RCPT_PRIMARY = EMAIL_CFG.get("recipients", {}).get("primary", "elias@o2data.com.br")
RCPT_BACKUP  = EMAIL_CFG.get("recipients", {}).get("backup",  "replikabackup@gmail.com")

RL_WINDOW    = SEC_CFG.get("rate_limit", {}).get("window_seconds", 60)
RL_MAX       = SEC_CFG.get("rate_limit", {}).get("max_requests", 120)
RL_MAX_API   = SEC_CFG.get("rate_limit", {}).get("max_api_requests", 20)
RL_BAN_THR   = SEC_CFG.get("rate_limit", {}).get("ban_threshold", 5)
RL_BAN_MIN   = SEC_CFG.get("rate_limit", {}).get("ban_duration_minutes", 60)
RL_WHITELIST = set(SEC_CFG.get("rate_limit", {}).get("whitelist_ips", ["127.0.0.1", "::1"]))
SQLI_PATS    = []
XSS_PATS     = []
SCANNER_PATS = []

for _p in SEC_CFG.get("sqli_patterns", []):
    try:
        SQLI_PATS.append(re.compile(_p, re.I))
    except re.error as _e:
        print(f"[WAF] sqli_pattern inválido ignorado: {_p!r} — {_e}")

for _p in SEC_CFG.get("xss_patterns", []):
    try:
        XSS_PATS.append(re.compile(_p, re.I))
    except re.error as _e:
        print(f"[WAF] xss_pattern inválido ignorado: {_p!r} — {_e}")

for _p in SEC_CFG.get("scanner_ua_patterns", []):
    try:
        SCANNER_PATS.append(re.compile(_p, re.I))
    except re.error as _e:
        print(f"[WAF] scanner_pattern inválido ignorado: {_p!r} — {_e}")


# ── Logging ───────────────────────────────────────────────────────────────────
log_file = LOG_DIR / "server.log"
_fh = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%Y-%m-%d %H:%M:%S"))
logging.basicConfig(level=logging.INFO, handlers=[_fh])
logger = logging.getLogger("o2")

_LEVEL_COLORS = {
    "info":    Fore.CYAN,
    "success": Fore.GREEN + Style.BRIGHT,
    "warn":    Fore.YELLOW + Style.BRIGHT,
    "error":   Fore.RED + Style.BRIGHT,
    "metric":  Fore.MAGENTA + Style.BRIGHT,
    "mail":    Fore.BLUE + Style.BRIGHT,
    "waf":     Fore.LIGHTRED_EX + Style.BRIGHT,
    "ban":     Fore.RED + Back.WHITE + Style.BRIGHT if HAS_COLOR else "",
    "visitor": Fore.LIGHTGREEN_EX,
    "req":     Fore.LIGHTBLUE_EX,
}

def clog(msg: str, level: str = "info", emoji: str = ""):
    c = _LEVEL_COLORS.get(level, Fore.WHITE)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    prefix = f"{emoji} " if emoji else ""
    line = f"{c}[{ts}] {prefix}{msg}{Style.RESET_ALL if HAS_COLOR else ''}"
    print(line)
    logger.info(f"[{level.upper()}] {emoji} {msg}")

# ── In-memory state ───────────────────────────────────────────────────────────
COUNTERS: Dict[str, Any] = {
    "requests_total": 0, "requests_200": 0, "requests_4xx": 0, "requests_5xx": 0,
    "leads_total": 0, "leads_email_ok": 0, "leads_email_err": 0,
    "waf_blocks": 0, "rate_limit_hits": 0, "ip_bans": 0,
    "visitors_unique": 0, "visitors_today": 0,
    "uptime_start": time.time(),
}
# Rate limit: {ip: deque of timestamps}
_RL_STORE: Dict[str, collections.deque] = {}
_RL_VIOLATIONS: Dict[str, int] = {}
# IP ban: {ip: unban_timestamp (0=permanent)}
_IP_BANS: Dict[str, float] = {}
_RL_LOCK = threading.Lock()
# Email queue
_EMAIL_QUEUE: queue.Queue = queue.Queue(maxsize=500)
# Event queue for async DB writes
_EVENT_QUEUE: queue.Queue = queue.Queue(maxsize=5000)
# Memory cache: {key: (value, expires_at)}
_CACHE: Dict[str, tuple] = {}
_CACHE_LOCK = threading.Lock()
# Thread pool
_EXECUTOR = ThreadPoolExecutor(max_workers=4)


# ── SQLite init ───────────────────────────────────────────────────────────────
def db_init():
    # Metrics DB
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, method TEXT, path TEXT,
            status INTEGER, duration_ms REAL, ip TEXT, ua TEXT
        );
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, name TEXT, company TEXT,
            email TEXT, phone TEXT, challenge TEXT, message TEXT, ip TEXT,
            email_sent INTEGER DEFAULT 0, consent INTEGER DEFAULT 1,
            marketing_consent INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS kpis (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, key TEXT, value REAL
        );
        CREATE TABLE IF NOT EXISTS waf_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, ip TEXT, ua TEXT,
            path TEXT, reason TEXT, action TEXT
        );
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            name TEXT,
            email TEXT,
            company TEXT,
            role TEXT,
            sector TEXT,
            employees TEXT,
            revenue TEXT,
            urgency TEXT,
            budget TEXT,
            main_challenge TEXT,
            area TEXT,
            scores TEXT,
            total_score REAL,
            max_score REAL,
            percentage REAL,
            ip TEXT,
            email_sent INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_req_ts ON requests(ts);
        CREATE INDEX IF NOT EXISTS idx_leads_ts ON leads(ts);
        CREATE INDEX IF NOT EXISTS idx_kpis_key ON kpis(key);
        CREATE INDEX IF NOT EXISTS idx_waf_ip ON waf_events(ip);
        CREATE INDEX IF NOT EXISTS idx_assess_ts ON assessments(ts);
        CREATE INDEX IF NOT EXISTS idx_assess_email ON assessments(email);
    """)
    con.commit(); con.close()

    # Visitors DB
    con = sqlite3.connect(VISITORS_DB)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vid TEXT UNIQUE, first_seen TEXT, last_seen TEXT,
            visit_count INTEGER DEFAULT 1, ip TEXT, country TEXT,
            browser TEXT, browser_version TEXT, os TEXT, os_version TEXT,
            device TEXT, screen TEXT, language TEXT, timezone TEXT,
            referrer TEXT, utm_source TEXT, utm_medium TEXT, utm_campaign TEXT,
            consent INTEGER DEFAULT 0, marketing_consent INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vid TEXT, ts TEXT, path TEXT, referrer TEXT,
            time_on_page INTEGER, scroll_depth INTEGER, ip TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vid TEXT, ts TEXT, event_type TEXT, data TEXT, ip TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_vis_vid ON visitors(vid);
        CREATE INDEX IF NOT EXISTS idx_vis_ip ON visitors(ip);
        CREATE INDEX IF NOT EXISTS idx_pv_vid ON page_views(vid);
    """)
    con.commit(); con.close()

    # Bans DB
    con = sqlite3.connect(BANS_DB)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS ip_bans (
            ip TEXT PRIMARY KEY, reason TEXT, banned_at TEXT,
            unban_at TEXT, permanent INTEGER DEFAULT 0, hit_count INTEGER DEFAULT 1
        );
    """)
    con.commit(); con.close()

    # Load existing bans into memory
    con = sqlite3.connect(BANS_DB)
    rows = con.execute("SELECT ip, unban_at, permanent FROM ip_bans").fetchall()
    con.close()
    for ip, unban_at, permanent in rows:
        if permanent:
            _IP_BANS[ip] = 0
        else:
            try:
                ts = datetime.datetime.fromisoformat(unban_at).timestamp()
                if ts > time.time():
                    _IP_BANS[ip] = ts
            except Exception:
                pass

    clog("SQLite inicializado (metrics + visitors + bans + assessments)", "success", "🗄️")

def _db_exec(db_path, sql, params=()):
    try:
        con = sqlite3.connect(db_path, check_same_thread=False)
        con.execute(sql, params); con.commit(); con.close()
    except Exception as e:
        logger.error(f"db_exec: {e}")


# ── WAF ───────────────────────────────────────────────────────────────────────
def waf_check(ip: str, path: str, ua: str, body: str = "") -> Optional[str]:
    """Returns reason string if blocked, None if OK."""
    # Scanner UA
    for pat in SCANNER_PATS:
        if pat.search(ua):
            return f"scanner_ua:{pat.pattern}"
    # SQLi in path/body
    target = path + " " + body
    for pat in SQLI_PATS:
        if pat.search(target):
            return f"sqli:{pat.pattern}"
    # XSS
    for pat in XSS_PATS:
        if pat.search(target):
            return f"xss:{pat.pattern}"
    # Path traversal
    if "../" in path or "..%2F" in path.upper() or "%2E%2E" in path.upper():
        return "path_traversal"
    # Suspicious paths
    suspicious = ["/etc/passwd", "/proc/", "/.env", "/wp-admin", "/phpmyadmin",
                  "/admin.php", "/.git/", "/config.php", "/shell", "/cmd"]
    for s in suspicious:
        if s.lower() in path.lower():
            return f"suspicious_path:{s}"
    return None

def is_banned(ip: str) -> bool:
    if ip in RL_WHITELIST:
        return False
    if ip not in _IP_BANS:
        return False
    unban_ts = _IP_BANS[ip]
    if unban_ts == 0:  # permanent
        return True
    if time.time() < unban_ts:
        return True
    del _IP_BANS[ip]  # expired
    return False

def ban_ip(ip: str, reason: str, permanent: bool = False, minutes: int = 60):
    if ip in RL_WHITELIST:
        return
    unban_ts = 0.0 if permanent else time.time() + minutes * 60
    _IP_BANS[ip] = unban_ts
    COUNTERS["ip_bans"] += 1
    unban_str = "PERMANENT" if permanent else datetime.datetime.fromtimestamp(unban_ts).isoformat()
    _db_exec(BANS_DB,
        "INSERT OR REPLACE INTO ip_bans(ip,reason,banned_at,unban_at,permanent) VALUES(?,?,?,?,?)",
        (ip, reason, datetime.datetime.utcnow().isoformat(), unban_str, int(permanent)))
    clog(f"IP BANIDO: {ip} | {reason} | ate: {unban_str}", "ban", "🚫")

def rate_limit_check(ip: str, is_api: bool = False) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    if ip in RL_WHITELIST:
        return True
    now = time.time()
    limit = RL_MAX_API if is_api else RL_MAX
    with _RL_LOCK:
        if ip not in _RL_STORE:
            _RL_STORE[ip] = collections.deque()
        dq = _RL_STORE[ip]
        # Remove old entries
        while dq and dq[0] < now - RL_WINDOW:
            dq.popleft()
        if len(dq) >= limit:
            COUNTERS["rate_limit_hits"] += 1
            _RL_VIOLATIONS[ip] = _RL_VIOLATIONS.get(ip, 0) + 1
            if _RL_VIOLATIONS[ip] >= RL_BAN_THR:
                ban_ip(ip, "rate_limit_exceeded", minutes=RL_BAN_MIN)
            return False
        dq.append(now)
        return True


# ── Visitor tracking ──────────────────────────────────────────────────────────
def parse_ua(ua: str) -> dict:
    """Simple UA parser without external deps."""
    browser, browser_ver, os_name, os_ver, device = "Unknown","","Unknown","","desktop"
    ua_lower = ua.lower()
    # Browser
    if "edg/" in ua_lower:
        browser = "Edge"
        m = re.search(r"edg/([\d.]+)", ua_lower)
        browser_ver = m.group(1) if m else ""
    elif "chrome/" in ua_lower and "chromium" not in ua_lower:
        browser = "Chrome"
        m = re.search(r"chrome/([\d.]+)", ua_lower)
        browser_ver = m.group(1) if m else ""
    elif "firefox/" in ua_lower:
        browser = "Firefox"
        m = re.search(r"firefox/([\d.]+)", ua_lower)
        browser_ver = m.group(1) if m else ""
    elif "safari/" in ua_lower and "chrome" not in ua_lower:
        browser = "Safari"
        m = re.search(r"version/([\d.]+)", ua_lower)
        browser_ver = m.group(1) if m else ""
    # OS
    if "windows nt" in ua_lower:
        os_name = "Windows"
        m = re.search(r"windows nt ([\d.]+)", ua_lower)
        os_ver = m.group(1) if m else ""
    elif "mac os x" in ua_lower:
        os_name = "macOS"
        m = re.search(r"mac os x ([\d_]+)", ua_lower)
        os_ver = m.group(1).replace("_", ".") if m else ""
    elif "android" in ua_lower:
        os_name = "Android"
        m = re.search(r"android ([\d.]+)", ua_lower)
        os_ver = m.group(1) if m else ""
        device = "mobile"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os_name = "iOS"
        device = "mobile" if "iphone" in ua_lower else "tablet"
    elif "linux" in ua_lower:
        os_name = "Linux"
    # Device
    if "tablet" in ua_lower or "ipad" in ua_lower:
        device = "tablet"
    elif "mobile" in ua_lower or "iphone" in ua_lower or "android" in ua_lower:
        device = "mobile"
    return {"browser": browser, "browser_version": browser_ver,
            "os": os_name, "os_version": os_ver, "device": device}

def get_or_create_visitor(vid: str, ip: str, ua: str, referrer: str, request: Request) -> str:
    """Upsert visitor record, return vid."""
    ua_info = parse_ua(ua)
    lang = request.headers.get("accept-language", "")[:20]
    utm = {k: request.query_params.get(k, "") for k in ["utm_source","utm_medium","utm_campaign"]}
    now = datetime.datetime.utcnow().isoformat()
    try:
        con = sqlite3.connect(VISITORS_DB, check_same_thread=False)
        existing = con.execute("SELECT id, visit_count FROM visitors WHERE vid=?", (vid,)).fetchone()
        if existing:
            con.execute("UPDATE visitors SET last_seen=?, visit_count=visit_count+1, ip=? WHERE vid=?",
                        (now, ip, vid))
        else:
            con.execute("""INSERT INTO visitors
                (vid,first_seen,last_seen,ip,browser,browser_version,os,os_version,
                 device,language,referrer,utm_source,utm_medium,utm_campaign)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (vid, now, now, ip,
                 ua_info["browser"], ua_info["browser_version"],
                 ua_info["os"], ua_info["os_version"], ua_info["device"],
                 lang[:20], referrer[:200],
                 utm["utm_source"], utm["utm_medium"], utm["utm_campaign"]))
            COUNTERS["visitors_unique"] += 1
        con.commit(); con.close()
    except Exception as e:
        logger.error(f"visitor upsert: {e}")
    return vid

def log_page_view(vid: str, path: str, referrer: str, ip: str):
    _db_exec(VISITORS_DB,
        "INSERT INTO page_views(vid,ts,path,referrer,ip) VALUES(?,?,?,?,?)",
        (vid, datetime.datetime.utcnow().isoformat(), path, referrer[:200], ip))

def append_visitor_log(vid: str, ip: str, ua: str, path: str, event: str):
    """Append to incremental YAML/JSON/MD logs."""
    entry = {
        "ts": datetime.datetime.utcnow().isoformat(),
        "vid": vid, "ip": ip, "ua": ua[:100], "path": path, "event": event
    }
    # YAML
    try:
        yf = DATA_DIR / "visitors_log.yaml"
        with open(yf, "a", encoding="utf-8") as f:
            f.write(f"- ts: {entry['ts']}\n  vid: {entry['vid']}\n  ip: {entry['ip']}\n"
                    f"  ua: \"{entry['ua']}\"\n  path: {entry['path']}\n  event: {entry['event']}\n")
    except Exception: pass
    # JSON (newline-delimited)
    try:
        jf = DATA_DIR / "visitors_log.json"
        with open(jf, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception: pass
    # MD
    try:
        mf = DATA_DIR / "visitors_log.md"
        with open(mf, "a", encoding="utf-8") as f:
            f.write(f"| {entry['ts']} | {entry['vid'][:8]} | {entry['ip']} | {entry['path']} | {entry['event']} |\n")
    except Exception: pass


# ── Email ─────────────────────────────────────────────────────────────────────
def send_email_sync(lead: dict) -> bool:
    """Email interno de lead — dark theme premium."""
    name      = lead.get("name", "")
    company   = lead.get("company", "")
    email     = lead.get("email", "")
    phone     = lead.get("phone", "")
    challenge = lead.get("challenge", "")
    message   = lead.get("message", "")
    ts        = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    subject   = f"[O2 Lead] {name} — {company} | {challenge}"

    msg_block = ""
    if message:
        msg_block = (
            f"<div style='margin-top:20px;padding:16px 18px;background:#0f172a;"
            f"border-radius:10px;border-left:4px solid #7c3aed'>"
            f"<p style='margin:0 0 6px;font-size:11px;font-weight:700;color:#a78bfa;"
            f"text-transform:uppercase;letter-spacing:.5px'>Mensagem</p>"
            f"<p style='margin:0;font-size:13px;color:#cbd5e1;line-height:1.6'>{message}</p>"
            f"</div>"
        )

    html = f"""<!DOCTYPE html>
<html lang='pt-BR'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'></head>
<body style='margin:0;padding:0;background:#060b18;font-family:Segoe UI,Arial,sans-serif'>
<table width='100%' cellpadding='0' cellspacing='0' style='background:#060b18;padding:32px 16px'>
<tr><td align='center'>
<table width='620' cellpadding='0' cellspacing='0' style='max-width:620px;width:100%'>
  <tr><td style='background:linear-gradient(135deg,#1e3a8a 0%,#5b21b6 100%);border-radius:16px 16px 0 0;padding:30px 36px'>
    <table width='100%' cellpadding='0' cellspacing='0'><tr>
      <td>
        <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:2px'>O2 Data Solutions — CRM Interno</p>
        <h1 style='margin:0;font-size:22px;font-weight:800;color:#fff'>🎯 Novo Lead Recebido</h1>
        <p style='margin:8px 0 0;font-size:12px;color:rgba(255,255,255,.65)'>{ts} · Formulário de Contato</p>
      </td>
      <td align='right' style='vertical-align:middle'>
        <div style='background:rgba(255,255,255,.12);border-radius:12px;padding:10px 14px;font-size:22px;line-height:1'>🎯</div>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style='background:#0d1526;padding:28px 36px'>
    <p style='margin:0 0 14px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.5px'>Dados do Contato</p>
    <table width='100%' cellpadding='0' cellspacing='0' style='border-collapse:collapse'>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>👤 Nome</span>
        <span style='font-size:15px;font-weight:700;color:#f1f5f9'>{name}</span>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>🏢 Empresa</span>
        <span style='font-size:15px;font-weight:700;color:#f1f5f9'>{company}</span>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>📧 E-mail</span>
        <a href='mailto:{email}' style='font-size:15px;font-weight:700;color:#60a5fa;text-decoration:none'>{email}</a>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a;border-bottom:1px solid #1e293b'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>📱 WhatsApp</span>
        <span style='font-size:15px;font-weight:700;color:#4ade80'>{phone or "—"}</span>
      </td></tr>
      <tr><td style='padding:12px 16px;background:#0f172a'>
        <span style='font-size:10px;color:#475569;display:block;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px'>🎯 Principal Desafio</span>
        <span style='font-size:15px;font-weight:700;color:#c084fc'>{challenge}</span>
      </td></tr>
    </table>
    {msg_block}
    <table width='100%' cellpadding='0' cellspacing='0' style='margin-top:24px'><tr>
      <td style='padding-right:6px' width='50%'>
        <a href='https://wa.me/5511913353137' style='display:block;background:#16a34a;color:#fff;padding:13px 16px;border-radius:10px;text-decoration:none;font-weight:700;font-size:13px;text-align:center'>💬 WhatsApp</a>
      </td>
      <td style='padding-left:6px' width='50%'>
        <a href='mailto:{email}?subject=Re: Contato O2 Data Solutions' style='display:block;background:#2563eb;color:#fff;padding:13px 16px;border-radius:10px;text-decoration:none;font-weight:700;font-size:13px;text-align:center'>📧 E-mail</a>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style='background:#060b18;border-radius:0 0 16px 16px;padding:18px 36px;border-top:1px solid #0d1526'>
    <p style='margin:0;font-size:11px;color:#334155;text-align:center'>
      O2 Data Solutions · Maringá, PR · <a href='mailto:contato@o2data.com.br' style='color:#3b82f6;text-decoration:none'>contato@o2data.com.br</a>
    </p>
  </td></tr>
</table></td></tr></table>
</body></html>"""

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as srv:
            srv.login(SMTP_USER, SMTP_PASS)
            for rcpt in [RCPT_PRIMARY, RCPT_BACKUP]:
                msg = MIMEMultipart("alternative")
                msg["Subject"]  = subject
                msg["From"]     = f"{SENDER_NAME} <{SENDER_EMAIL}>"
                msg["To"]       = rcpt
                msg["Reply-To"] = email
                msg.attach(MIMEText(html, "html", "utf-8"))
                srv.sendmail(SENDER_EMAIL, rcpt, msg.as_string())
        clog(f"Lead email → {RCPT_PRIMARY} + {RCPT_BACKUP}", "mail", "✅")
        return True
    except Exception as e:
        clog(f"Lead email ERRO: {e}", "error", "❌")
        return False


def send_assessment_email_sync(data: dict) -> bool:
    """Envia email de assessment: interno (dark) + cliente (light)."""
    name     = data.get("name", "")
    email    = data.get("email", "")
    company  = data.get("company", "")
    role     = data.get("role", "")
    sector   = data.get("sector", "")
    employees= data.get("employees", "")
    revenue  = data.get("revenue", "")
    urgency  = data.get("urgency", "")
    budget   = data.get("budget", "")
    challenge= data.get("main_challenge", "")
    area     = data.get("area", "")
    pct      = data.get("percentage", 0)
    avg      = data.get("total_score", 0)
    scores   = data.get("scores", {})
    ts       = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    # ── helpers locais de HTML ──────────────────────────────────────────────
    import sys as _sys
    _sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent / "assets" / "js"))
    try:
        import email_data as _ED
        _Q = _ED.QUESTION_LABELS
        _R = _ED.RECOMMENDATIONS
        _AL = _ED.AREA_LABELS
        _AI = _ED.AREA_ICONS_EMOJI
        _AC = _ED.AREA_COLORS
    except ImportError:
        _Q = {}; _R = {}
        _AL = {"supply_chain":"Supply Chain & Compras","comercial":"Inteligencia Comercial & RevOps",
               "credito_risco":"Credito & Risco","dados_ml":"Dados & Machine Learning",
               "automacao":"Automacao, RPA & Alertas","dashboards":"Dashboards & Analytics"}
        _AI = {"supply_chain":"🚚","comercial":"📈","credito_risco":"🛡️",
               "dados_ml":"��","automacao":"🤖","dashboards":"📊"}
        _AC = {"supply_chain":"#3b82f6","comercial":"#8b5cf6","credito_risco":"#ef4444",
               "dados_ml":"#06b6d4","automacao":"#f59e0b","dashboards":"#22c55e"}

    def _srows_int(sc):
        rows = []
        for qid, sv in sc.items():
            lbl = _Q.get(qid, qid)
            bc = "#ef4444" if sv <= 3 else "#f59e0b" if sv <= 6 else "#22c55e"
            bp = sv * 10
            rows.append(
                f'<tr><td style="padding:7px 0;font-size:12px;color:#94a3b8;width:55%;border-bottom:1px solid #1e293b">{lbl}</td>'
                f'<td style="padding:7px 8px;width:35%;border-bottom:1px solid #1e293b">'
                f'<div style="background:#1e293b;border-radius:4px;height:7px;overflow:hidden">'
                f'<div style="width:{bp}%;height:7px;background:{bc};border-radius:4px"></div></div></td>'
                f'<td style="padding:7px 0;text-align:right;font-weight:700;font-size:12px;color:{bc};border-bottom:1px solid #1e293b">{sv:.1f}/10</td></tr>'
            )
        return "".join(rows)

    def _srows_cli(sc):
        rows = []
        for qid, sv in sc.items():
            lbl = _Q.get(qid, qid)
            bc = "#ef4444" if sv <= 3 else "#f59e0b" if sv <= 6 else "#22c55e"
            bp = sv * 10
            rows.append(
                f'<tr><td style="padding:8px 0;font-size:13px;color:#475569;width:55%;border-bottom:1px solid #e2e8f0">{lbl}</td>'
                f'<td style="padding:8px 8px;width:35%;border-bottom:1px solid #e2e8f0">'
                f'<div style="background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden">'
                f'<div style="width:{bp}%;height:8px;background:{bc};border-radius:4px"></div></div></td>'
                f'<td style="padding:8px 0;text-align:right;font-weight:700;font-size:13px;color:{bc};border-bottom:1px solid #e2e8f0">{sv:.1f}/10</td></tr>'
            )
        return "".join(rows)

    def _recs_int(ar, lk):
        recs = _R.get(ar, {}).get(lk, [])
        if not recs: return ""
        items = "".join(
            f'<li style="margin-bottom:10px;padding:10px 12px;background:#0f172a;border-radius:8px;'
            f'border-left:3px solid #3b82f6;font-size:12px;color:#cbd5e1;line-height:1.5">{r}</li>'
            for r in recs
        )
        return (
            f'<div style="margin-top:24px">'
            f'<p style="margin:0 0 12px;font-size:10px;font-weight:700;color:#475569;'
            f'text-transform:uppercase;letter-spacing:1.5px">&#x1F4CB; Recomendacoes Prioritarias</p>'
            f'<ul style="margin:0;padding:0;list-style:none">{items}</ul></div>'
        )

    def _recs_cli(ar, lk):
        recs = _R.get(ar, {}).get(lk, [])
        if not recs: return ""
        items = "".join(
            f'<li style="margin-bottom:12px;padding:14px 16px;background:#f8fafc;border-radius:10px;'
            f'border-left:4px solid #2563eb;font-size:13px;color:#334155;line-height:1.6">'
            f'<span style="font-weight:700;color:#1d4ed8">&#x2192;</span> {r}</li>'
            for r in recs
        )
        return (
            f'<div style="margin-top:28px">'
            f'<p style="margin:0 0 14px;font-size:14px;font-weight:700;color:#1e293b">'
            f'&#x1F3AF; Recomendacoes Prioritarias para Voce</p>'
            f'<ul style="margin:0;padding:0;list-style:none">{items}</ul></div>'
        )

    area_label = _AL.get(area, area)
    area_icon  = _AI.get(area, "📊")
    area_color = _AC.get(area, "#2563eb")

    # Nivel de maturidade
    if avg <= 3.9:
        level_label = "Critico"; level_color = "#ef4444"; level_bg_int = "#1a0a0a"; level_bg_cli = "#fef2f2"
        level_msg_int = "Oportunidades imediatas de melhoria com alto impacto. Prioridade maxima."
        level_msg_cli = "Sua empresa esta nos estagios iniciais da jornada analitica. Ha oportunidades significativas de melhoria que podem gerar retorno rapido."
        level_key = "critico"
    elif avg <= 6.9:
        level_label = "Em Desenvolvimento"; level_color = "#f59e0b"; level_bg_int = "#1a1200"; level_bg_cli = "#fffbeb"
        level_msg_int = "Jornada iniciada, lacunas importantes identificadas. Potencial de aceleracao alto."
        level_msg_cli = "Voce ja iniciou a jornada analitica. Com as iniciativas certas, pode acelerar significativamente os resultados."
        level_key = "desenvolvimento"
    else:
        level_label = "Avancado"; level_color = "#22c55e"; level_bg_int = "#0a1a0a"; level_bg_cli = "#f0fdf4"
        level_msg_int = "Maturidade elevada. Foco em otimizacao, escala e tecnologias emergentes."
        level_msg_cli = "Sua empresa demonstra maturidade analitica elevada. O foco agora e otimizar, escalar e explorar IA generativa."
        level_key = "avancado"

    score_rows_int = _srows_int(scores)
    score_rows_cli = _srows_cli(scores)
    recs_int_html  = _recs_int(area, level_key)
    recs_cli_html  = _recs_cli(area, level_key)

    subject_int = f"[O2 Assessment] {name} — {area_label} | Score: {avg:.1f}/10 ({level_label})"
    subject_cli = f"Seu Diagnostico de Maturidade Analitica — {area_label} | O2 Data Solutions"

    # ── HTML INTERNO (dark theme) ─────────────────────────────────────────────
    html_int = f"""<!DOCTYPE html>
<html lang='pt-BR'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'></head>
<body style='margin:0;padding:0;background:#060b18;font-family:Segoe UI,Arial,sans-serif'>
<table width='100%' cellpadding='0' cellspacing='0' style='background:#060b18;padding:32px 16px'>
<tr><td align='center'>
<table width='660' cellpadding='0' cellspacing='0' style='max-width:660px;width:100%'>

  <!-- HEADER -->
  <tr><td style='background:linear-gradient(135deg,#1e3a8a 0%,#5b21b6 100%);border-radius:16px 16px 0 0;padding:28px 36px'>
    <table width='100%' cellpadding='0' cellspacing='0'><tr>
      <td>
        <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:2px'>O2 Data Solutions — Assessment Interno</p>
        <h1 style='margin:0;font-size:21px;font-weight:800;color:#fff'>📊 Diagnostico de Maturidade Analitica</h1>
        <p style='margin:8px 0 0;font-size:12px;color:rgba(255,255,255,.6)'>{ts} · {area_icon} {area_label}</p>
      </td>
      <td align='right' style='vertical-align:middle'>
        <div style='background:rgba(255,255,255,.1);border-radius:12px;padding:10px 14px;font-size:28px;line-height:1'>{area_icon}</div>
      </td>
    </tr></table>
  </td></tr>

  <!-- SCORE BADGE -->
  <tr><td style='background:#0d1526;padding:24px 36px 0'>
    <table width='100%' cellpadding='0' cellspacing='0'>
      <tr>
        <td style='background:{level_bg_int};border:1px solid {level_color}33;border-radius:12px;padding:20px 24px' width='48%'>
          <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:{level_color};text-transform:uppercase;letter-spacing:1px'>Score Geral</p>
          <p style='margin:0;font-size:42px;font-weight:900;color:{level_color};line-height:1'>{avg:.1f}<span style='font-size:18px;color:#475569'>/10</span></p>
          <p style='margin:6px 0 0;font-size:13px;font-weight:700;color:{level_color}'>{level_label}</p>
          <p style='margin:4px 0 0;font-size:11px;color:#64748b'>{pct:.0f}% de maturidade</p>
        </td>
        <td width='4%'></td>
        <td style='background:#0f172a;border-radius:12px;padding:20px 24px;vertical-align:top' width='48%'>
          <p style='margin:0 0 8px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px'>Perfil</p>
          <p style='margin:0 0 4px;font-size:14px;font-weight:700;color:#f1f5f9'>{name}</p>
          <p style='margin:0 0 4px;font-size:12px;color:#94a3b8'>{company}</p>
          <p style='margin:0 0 4px;font-size:11px;color:#64748b'>{role or "—"} · {sector or "—"}</p>
          <p style='margin:0 0 4px;font-size:11px;color:#64748b'>{employees or "—"} func. · {revenue or "—"}</p>
          <p style='margin:0;font-size:11px;color:#64748b'>Urgencia: {urgency or "—"} · Budget: {budget or "—"}</p>
        </td>
      </tr>
    </table>
    <p style='margin:16px 0 0;font-size:12px;color:#64748b;font-style:italic'>{level_msg_int}</p>
  </td></tr>

  <!-- CONTATO -->
  <tr><td style='background:#0d1526;padding:20px 36px 0'>
    <p style='margin:0 0 12px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.5px'>Contato</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      <tr>
        <td style='padding-right:6px' width='50%'>
          <a href='mailto:{email}' style='display:block;background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:12px 14px;text-decoration:none'>
            <span style='font-size:10px;color:#475569;display:block;margin-bottom:2px'>📧 E-mail</span>
            <span style='font-size:13px;font-weight:700;color:#60a5fa'>{email}</span>
          </a>
        </td>
        <td style='padding-left:6px' width='50%'>
          <a href='https://wa.me/5511913353137' style='display:block;background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:12px 14px;text-decoration:none'>
            <span style='font-size:10px;color:#475569;display:block;margin-bottom:2px'>💬 Responder</span>
            <span style='font-size:13px;font-weight:700;color:#4ade80'>WhatsApp</span>
          </a>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- SCORES POR QUESTAO -->
  <tr><td style='background:#0d1526;padding:24px 36px 0'>
    <p style='margin:0 0 14px;font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.5px'>📈 Pontuacao por Questao — {area_label}</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      {score_rows_int}
    </table>
  </td></tr>

  <!-- RECOMENDACOES -->
  <tr><td style='background:#0d1526;padding:0 36px 28px'>
    {recs_int_html}
  </td></tr>

  <!-- FOOTER -->
  <tr><td style='background:#060b18;border-radius:0 0 16px 16px;padding:18px 36px;border-top:1px solid #0d1526'>
    <p style='margin:0;font-size:11px;color:#334155;text-align:center'>
      O2 Data Solutions · Maringa, PR · <a href='mailto:contato@o2data.com.br' style='color:#3b82f6;text-decoration:none'>contato@o2data.com.br</a>
    </p>
  </td></tr>

</table></td></tr></table>
</body></html>"""

    # ── HTML CLIENTE (light theme) ────────────────────────────────────────────
    html_cli = f"""<!DOCTYPE html>
<html lang='pt-BR'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'></head>
<body style='margin:0;padding:0;background:#f1f5f9;font-family:Segoe UI,Arial,sans-serif'>
<table width='100%' cellpadding='0' cellspacing='0' style='background:#f1f5f9;padding:32px 16px'>
<tr><td align='center'>
<table width='640' cellpadding='0' cellspacing='0' style='max-width:640px;width:100%'>

  <!-- HEADER -->
  <tr><td style='background:linear-gradient(135deg,#1e40af 0%,#6d28d9 100%);border-radius:16px 16px 0 0;padding:32px 36px'>
    <p style='margin:0 0 4px;font-size:10px;font-weight:700;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:2px'>O2 Data Solutions</p>
    <h1 style='margin:0;font-size:22px;font-weight:800;color:#fff;line-height:1.2'>Seu Diagnostico de Maturidade Analitica</h1>
    <p style='margin:10px 0 0;font-size:13px;color:rgba(255,255,255,.75)'>{area_icon} {area_label} · {ts}</p>
  </td></tr>

  <!-- SAUDACAO -->
  <tr><td style='background:#fff;padding:28px 36px 0'>
    <p style='margin:0;font-size:15px;color:#334155;line-height:1.6'>
      Ola, <strong>{name}</strong>! Obrigado por completar o diagnostico de maturidade analitica da <strong>{company}</strong>.
      Abaixo voce encontra seu resultado completo com recomendacoes personalizadas.
    </p>
  </td></tr>

  <!-- SCORE -->
  <tr><td style='background:#fff;padding:24px 36px 0'>
    <div style='background:{level_bg_cli};border:2px solid {level_color}33;border-radius:14px;padding:24px 28px'>
      <table width='100%' cellpadding='0' cellspacing='0'><tr>
        <td style='vertical-align:middle' width='30%'>
          <div style='text-align:center'>
            <div style='font-size:52px;font-weight:900;color:{level_color};line-height:1'>{avg:.1f}</div>
            <div style='font-size:12px;color:#64748b;font-weight:600'>de 10</div>
          </div>
        </td>
        <td style='padding-left:20px;vertical-align:middle'>
          <p style='margin:0 0 6px;font-size:18px;font-weight:800;color:{level_color}'>{level_label}</p>
          <p style='margin:0 0 8px;font-size:13px;color:#475569;line-height:1.5'>{level_msg_cli}</p>
          <div style='background:#e2e8f0;border-radius:6px;height:10px;overflow:hidden;margin-top:10px'>
            <div style='width:{pct:.0f}%;height:10px;background:{level_color};border-radius:6px'></div>
          </div>
          <p style='margin:6px 0 0;font-size:11px;color:#64748b;font-weight:600'>{pct:.0f}% de maturidade analitica</p>
        </td>
      </tr></table>
    </div>
  </td></tr>

  <!-- AREA AVALIADA -->
  <tr><td style='background:#fff;padding:20px 36px 0'>
    <div style='background:#f8fafc;border-radius:10px;padding:16px 20px;border-left:4px solid {area_color}'>
      <p style='margin:0 0 4px;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px'>Area Avaliada</p>
      <p style='margin:0;font-size:16px;font-weight:700;color:#1e293b'>{area_icon} {area_label}</p>
    </div>
  </td></tr>

  <!-- SCORES POR QUESTAO -->
  <tr><td style='background:#fff;padding:24px 36px 0'>
    <p style='margin:0 0 14px;font-size:14px;font-weight:700;color:#1e293b'>📈 Sua Pontuacao por Dimensao</p>
    <table width='100%' cellpadding='0' cellspacing='0'>
      {score_rows_cli}
    </table>
  </td></tr>

  <!-- RECOMENDACOES -->
  <tr><td style='background:#fff;padding:0 36px 28px'>
    {recs_cli_html}
  </td></tr>

  <!-- CTA -->
  <tr><td style='background:#f8fafc;padding:28px 36px;border-top:1px solid #e2e8f0;text-align:center'>
    <p style='margin:0 0 8px;font-size:15px;font-weight:700;color:#1e293b'>Quer um roadmap personalizado para sua empresa?</p>
    <p style='margin:0 0 20px;font-size:13px;color:#64748b;line-height:1.5'>
      Nossa equipe pode criar um plano de acao detalhado com base no seu diagnostico,
      priorizando as iniciativas de maior impacto para o seu negocio.
    </p>
    <a href='https://wa.me/5511913353137?text=Ola%21+Fiz+o+diagnostico+de+maturidade+analitica+e+gostaria+de+agendar+uma+reuniao+de+diagnostico.'
       style='display:inline-block;background:linear-gradient(135deg,#1e40af,#6d28d9);color:#fff;padding:16px 32px;border-radius:50px;text-decoration:none;font-weight:700;font-size:15px'>
      📅 Agendar Reunião de Diagnóstico
    </a>
    <p style='margin:16px 0 0;font-size:12px;color:#94a3b8'>Resposta em ate 24 horas uteis</p>
  </td></tr>

  <!-- FOOTER -->
  <tr><td style='background:#f1f5f9;border-radius:0 0 16px 16px;padding:20px 36px;border-top:1px solid #e2e8f0'>
    <p style='margin:0;font-size:11px;color:#94a3b8;text-align:center'>
      O2 Data Solutions · Maringa, PR · <a href='mailto:contato@o2data.com.br' style='color:#2563eb;text-decoration:none'>contato@o2data.com.br</a> · (11) 9 1335-3137
    </p>
    <p style='margin:8px 0 0;font-size:10px;color:#cbd5e1;text-align:center'>
      Voce recebeu este email porque completou o diagnostico de maturidade analitica em nosso site.
    </p>
  </td></tr>

</table></td></tr></table>
</body></html>"""

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as srv:
            srv.login(SMTP_USER, SMTP_PASS)
            # Email interno (dark)
            for rcpt in [RCPT_PRIMARY, RCPT_BACKUP]:
                msg = MIMEMultipart("alternative")
                msg["Subject"]  = subject_int
                msg["From"]     = f"{SENDER_NAME} <{SENDER_EMAIL}>"
                msg["To"]       = rcpt
                msg["Reply-To"] = email
                msg.attach(MIMEText(html_int, "html", "utf-8"))
                srv.sendmail(SENDER_EMAIL, rcpt, msg.as_string())
            # Email cliente (light)
            if email:
                msg_cli = MIMEMultipart("alternative")
                msg_cli["Subject"]  = subject_cli
                msg_cli["From"]     = f"{SENDER_NAME} <{SENDER_EMAIL}>"
                msg_cli["To"]       = email
                msg_cli.attach(MIMEText(html_cli, "html", "utf-8"))
                srv.sendmail(SENDER_EMAIL, email, msg_cli.as_string())
        clog(f"Assessment email → {name} | {area_label} | {avg:.1f}/10 ({level_label})", "mail", "📊")
        return True
    except Exception as e:
        clog(f"Assessment email ERRO: {e}", "error", "❌")
        return False


def email_worker():
    """Background thread consuming email queue."""
    while True:
        try:
            lead = _EMAIL_QUEUE.get(timeout=5)
            if lead.get("_type") == "assessment":
                send_assessment_email_sync(lead)
            else:
                send_email_sync(lead)
            _EMAIL_QUEUE.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"email_worker: {e}")

def event_worker():
    """Background thread flushing event queue to DB."""
    while True:
        try:
            ev = _EVENT_QUEUE.get(timeout=2)
            ev_type = ev.get("type")
            if ev_type == "request":
                _db_exec(DB_PATH,
                    "INSERT INTO requests(ts,method,path,status,duration_ms,ip,ua) VALUES(?,?,?,?,?,?,?)",
                    (ev["ts"],ev["method"],ev["path"],ev["status"],ev["ms"],ev["ip"],ev["ua"]))
            elif ev_type == "lead":
                d = ev["data"]
                _db_exec(DB_PATH,
                    "INSERT INTO leads(ts,name,company,email,phone,challenge,message,ip,email_sent,consent,marketing_consent) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (ev["ts"],d.get("name"),d.get("company"),d.get("email"),d.get("phone"),
                     d.get("challenge"),d.get("message"),ev["ip"],int(ev["email_ok"]),1,1))
            elif ev_type == "assessment":
                d = ev["data"]
                _db_exec(DB_PATH,
                    """INSERT INTO assessments(ts,name,email,company,role,sector,employees,revenue,
                       urgency,budget,main_challenge,area,scores,total_score,max_score,percentage,ip,email_sent)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (ev["ts"], d.get("name"), d.get("email"), d.get("company"),
                     d.get("role",""), d.get("sector",""), d.get("employees",""),
                     d.get("revenue",""), d.get("urgency",""), d.get("budget",""),
                     d.get("main_challenge",""), d.get("area",""),
                     json.dumps(d.get("scores",{}), ensure_ascii=False),
                     d.get("total_score",0), d.get("max_score",0), d.get("percentage",0),
                     ev["ip"], int(ev.get("email_ok", False))))
            elif ev_type == "kpi":
                _db_exec(DB_PATH, "INSERT INTO kpis(ts,key,value) VALUES(?,?,?)",
                         (ev["ts"],ev["key"],ev["value"]))
            elif ev_type == "waf":
                _db_exec(DB_PATH,
                    "INSERT INTO waf_events(ts,ip,ua,path,reason,action) VALUES(?,?,?,?,?,?)",
                    (ev["ts"],ev["ip"],ev["ua"],ev["path"],ev["reason"],ev["action"]))
            _EVENT_QUEUE.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"event_worker: {e}")

def push_event(ev: dict):
    ev["ts"] = datetime.datetime.utcnow().isoformat()
    try:
        _EVENT_QUEUE.put_nowait(ev)
    except queue.Full:
        logger.warning("event_queue full, dropping event")


# ── Console KPI dashboard (Rich) ──────────────────────────────────────────────
def _kpi_table() -> str:
    uptime = int(time.time() - COUNTERS["uptime_start"])
    h, m, s = uptime//3600, (uptime%3600)//60, uptime%60
    lines = [
        f"  🕐 Uptime      {h:02d}:{m:02d}:{s:02d}",
        f"  🌐 Requests    {COUNTERS['requests_total']}",
        f"  ✅ 2xx         {COUNTERS['requests_200']}",
        f"  ⚠️  4xx         {COUNTERS['requests_4xx']}",
        f"  ❌ 5xx         {COUNTERS['requests_5xx']}",
        f"  🎯 Leads       {COUNTERS['leads_total']}",
        f"  📧 Email OK    {COUNTERS['leads_email_ok']}",
        f"  📧 Email ERR   {COUNTERS['leads_email_err']}",
        f"  🛡️  WAF Blocks  {COUNTERS['waf_blocks']}",
        f"  🚦 Rate Hits   {COUNTERS['rate_limit_hits']}",
        f"  🚫 IP Bans     {COUNTERS['ip_bans']}",
        f"  👁️  Visitors    {COUNTERS['visitors_unique']}",
        f"  📋 Queue       {_EVENT_QUEUE.qsize()}",
        f"  📬 Email Q     {_EMAIL_QUEUE.qsize()}",
    ]
    return "\n".join(lines)

def kpi_ticker():
    """Background thread printing KPI panel every second."""
    import shutil
    while True:
        time.sleep(1)
        try:
            cols = shutil.get_terminal_size((120, 40)).columns
            if HAS_RICH and rich_console:
                pass  # Rich Live handles it separately
            else:
                # Simple colorama KPI line
                uptime = int(time.time() - COUNTERS["uptime_start"])
                line = (
                    f"{Fore.CYAN}⏱{uptime}s{Style.RESET_ALL} "
                    f"{Fore.GREEN}✅{COUNTERS['requests_200']}{Style.RESET_ALL} "
                    f"{Fore.RED}❌{COUNTERS['requests_5xx']}{Style.RESET_ALL} "
                    f"{Fore.MAGENTA}🎯{COUNTERS['leads_total']}{Style.RESET_ALL} "
                    f"{Fore.LIGHTRED_EX}🛡{COUNTERS['waf_blocks']}{Style.RESET_ALL} "
                    f"{Fore.YELLOW}🚦{COUNTERS['rate_limit_hits']}{Style.RESET_ALL} "
                    f"{Fore.LIGHTGREEN_EX}👁{COUNTERS['visitors_unique']}{Style.RESET_ALL}"
                )
                print(f"\r{line}", end="", flush=True)
        except Exception:
            pass


# ── Pydantic models ───────────────────────────────────────────────────────────
class ContactForm(BaseModel):
    name: str
    company: str
    email: str
    phone: Optional[str] = ""
    challenge: str
    message: Optional[str] = ""

class VisitorEvent(BaseModel):
    event: str
    path: Optional[str] = "/"
    data: Optional[dict] = {}

class AssessmentForm(BaseModel):
    # Perfil
    name: str
    email: str
    company: str
    role: Optional[str] = ""
    sector: Optional[str] = ""
    employees: Optional[str] = ""
    revenue: Optional[str] = ""
    urgency: Optional[str] = ""
    budget: Optional[str] = ""
    main_challenge: Optional[str] = ""
    # Questionário
    area: str
    scores: dict          # {question_id: score_0_to_10}
    total_score: float
    max_score: float
    percentage: float

# ── Security headers ──────────────────────────────────────────────────────────
SEC_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    # Start background workers
    threading.Thread(target=email_worker, daemon=True, name="email-worker").start()
    threading.Thread(target=event_worker, daemon=True, name="event-worker").start()
    threading.Thread(target=kpi_ticker,   daemon=True, name="kpi-ticker").start()

    # Init MD log header if new
    mf = DATA_DIR / "visitors_log.md"
    if not mf.exists():
        mf.write_text("| Timestamp | VID | IP | Path | Event |\n|---|---|---|---|---|\n", encoding="utf-8")

    clog("=" * 60, "info")
    clog("  🚀  O2 Data Solutions — Server v2 iniciado", "success")
    clog(f"  🌐  http://0.0.0.0:{PORT}", "info")
    clog(f"  📚  Docs: http://localhost:{PORT}/docs", "info")
    clog(f"  📊  Métricas: http://localhost:{PORT}/api/metrics", "metric")
    clog(f"  🛡️   WAF: ATIVO | Rate Limit: {RL_MAX}req/{RL_WINDOW}s", "waf")
    clog(f"  🗄️   DBs: metrics + visitors + bans + assessments", "info")
    clog(f"  🔄  Hot Reload: ATIVO (HTML/CSS/JS/YAML)", "info")
    clog("=" * 60, "info")
    yield
    clog("🛑  Server encerrado", "warn")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="O2 Data Solutions",
    description="Landing page B2B + WAF + Security + Analytics",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Main middleware: WAF + Rate Limit + Logging + Visitor ─────────────────────
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    t0 = time.perf_counter()
    ip = request.client.host if request.client else "0.0.0.0"
    ua = request.headers.get("user-agent", "")[:200]
    path = request.url.path
    referrer = request.headers.get("referer", "")

    # ── IP Ban check ──────────────────────────────────────────
    if is_banned(ip):
        COUNTERS["waf_blocks"] += 1
        clog(f"BLOCKED (banned): {ip} {path}", "ban", "🚫")
        return JSONResponse({"error": "Access denied"}, status_code=403,
                            headers={**SEC_HEADERS, "X-Block-Reason": "ip_banned"})

    # ── WAF check ─────────────────────────────────────────────
    body_str = ""
    if request.method in ("POST", "PUT", "PATCH"):
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8", errors="ignore")[:2000]
        except Exception:
            pass

    waf_reason = waf_check(ip, path, ua, body_str)
    if waf_reason:
        COUNTERS["waf_blocks"] += 1
        auto_ban = any(k in waf_reason for k in ["sqli", "xss", "scanner", "path_traversal"])
        if auto_ban:
            ban_ip(ip, waf_reason, minutes=RL_BAN_MIN)
        push_event({"type":"waf","ip":ip,"ua":ua[:100],"path":path,"reason":waf_reason,"action":"block"})
        clog(f"WAF BLOCK: {ip} | {waf_reason} | {path[:60]}", "waf", "🛡️")
        return JSONResponse({"error": "Request blocked by WAF"}, status_code=403,
                            headers={**SEC_HEADERS, "X-Block-Reason": waf_reason[:50]})

    # ── Rate limit ────────────────────────────────────────────
    is_api = path.startswith("/api")
    if not rate_limit_check(ip, is_api):
        clog(f"RATE LIMIT: {ip} {path}", "warn", "🚦")
        return JSONResponse({"error": "Too many requests"}, status_code=429,
                            headers={**SEC_HEADERS, "Retry-After": str(RL_WINDOW)})

    # ── Visitor tracking ──────────────────────────────────────
    vid = request.cookies.get("o2_vid") or str(uuid.uuid4())
    if path in ("/", "/index.html") or path.endswith(".html"):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(_EXECUTOR, get_or_create_visitor, vid, ip, ua, referrer, request)
        loop.run_in_executor(_EXECUTOR, log_page_view, vid, path, referrer, ip)
        loop.run_in_executor(_EXECUTOR, append_visitor_log, vid, ip, ua, path, "pageview")

    # ── Process request ───────────────────────────────────────
    response = await call_next(request)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    status = response.status_code

    # Add security headers
    for k, v in SEC_HEADERS.items():
        response.headers[k] = v

    # No-cache for JS/CSS/HTML to prevent stale file issues
    if path.endswith((".js", ".css", ".html")) or path in ("/", "/index.html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"]        = "no-cache"
        response.headers["Expires"]       = "0"

    # Set visitor cookie (1 year)
    if "o2_vid" not in request.cookies:
        response.set_cookie("o2_vid", vid, max_age=365*86400, samesite="lax", httponly=False)

    # Counters
    COUNTERS["requests_total"] += 1
    if 200 <= status < 300: COUNTERS["requests_200"] += 1
    elif 400 <= status < 500: COUNTERS["requests_4xx"] += 1
    elif status >= 500: COUNTERS["requests_5xx"] += 1

    # Log (only API + main pages)
    if is_api or path in ("/", "/index.html"):
        sc = Fore.GREEN if status < 400 else Fore.RED
        clog(f"{sc}{request.method:6} {status} {path:45} {ms:7.1f}ms  {ip}", "req")

    # Async DB log
    push_event({"type":"request","method":request.method,"path":path,
                "status":status,"ms":ms,"ip":ip,"ua":ua[:100]})

    return response


# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/assets",   StaticFiles(directory=BASE_DIR/"assets"),   name="assets")
app.mount("/partials", StaticFiles(directory=BASE_DIR/"partials"), name="partials")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(BASE_DIR/"index.html", media_type="text/html")

@app.get("/waf-challenge", include_in_schema=False)
async def waf_challenge_page():
    html = (BASE_DIR/"partials"/"waf.html")
    if html.exists():
        return FileResponse(html, media_type="text/html")
    return HTMLResponse("<h1>Security Check</h1>", status_code=200)

@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    target = BASE_DIR / full_path
    if target.is_file():
        return FileResponse(target)
    return FileResponse(BASE_DIR/"index.html", media_type="text/html")

# ── API: contact ──────────────────────────────────────────────────────────────
@app.post("/api/contact")
async def contact(form: ContactForm, request: Request):
    ip = request.client.host if request.client else "?"
    clog(f"Lead: {form.name} | {form.company} | {form.email} | {form.challenge}", "success", "🎯")
    # Queue email (non-blocking)
    try:
        _EMAIL_QUEUE.put_nowait(form.dict())
    except queue.Full:
        clog("Email queue full!", "warn", "⚠️")
    # Queue DB write
    push_event({"type":"lead","data":form.dict(),"ip":ip,"email_ok":True})
    push_event({"type":"kpi","key":"lead_received","value":1})
    COUNTERS["leads_total"] += 1
    COUNTERS["leads_email_ok"] += 1
    # Log visitor event
    vid = request.cookies.get("o2_vid", "unknown")
    _EXECUTOR.submit(append_visitor_log, vid, ip, "", "/api/contact", "lead_submit")
    return JSONResponse({"ok": True, "message": "Lead recebido com sucesso!"})

# ── API: assessment ───────────────────────────────────────────────────────────
@app.post("/api/assessment")
async def assessment(form: AssessmentForm, request: Request):
    ip = request.client.host if request.client else "?"
    avg = round(form.total_score, 2)

    # Score level
    if avg <= 3.9:
        level = "Crítico"
    elif avg <= 6.9:
        level = "Em Desenvolvimento"
    else:
        level = "Avançado"

    clog(
        f"Assessment: {form.name} | {form.company} | {form.area} | "
        f"Score: {avg:.1f}/10 ({level}) | {form.percentage:.0f}%",
        "success", "📊"
    )

    # Queue email (non-blocking)
    email_payload = form.dict()
    email_payload["_type"] = "assessment"
    try:
        _EMAIL_QUEUE.put_nowait(email_payload)
        email_ok = True
    except queue.Full:
        clog("Email queue full (assessment)!", "warn", "⚠️")
        email_ok = False

    # Queue DB write
    push_event({
        "type": "assessment",
        "data": form.dict(),
        "ip": ip,
        "email_ok": email_ok,
    })
    push_event({"type": "kpi", "key": "assessment_received", "value": 1})
    push_event({"type": "kpi", "key": f"assessment_{form.area}", "value": avg})

    # Log visitor event
    vid = request.cookies.get("o2_vid", "unknown")
    _EXECUTOR.submit(append_visitor_log, vid, ip, "", "/api/assessment", "assessment_submit")

    # Build recommendations based on level
    area_labels = {
        "supply_chain": "Supply Chain & Compras",
        "comercial": "Inteligência Comercial & RevOps",
        "credito_risco": "Crédito & Risco",
        "dados_ml": "Dados & Machine Learning",
        "automacao": "Automação, RPA & Alertas",
        "dashboards": "Dashboards & Analytics",
    }

    return JSONResponse({
        "ok": True,
        "message": "Diagnóstico recebido! Verifique seu e-mail para o relatório completo.",
        "result": {
            "area": form.area,
            "area_label": area_labels.get(form.area, form.area),
            "score": avg,
            "percentage": form.percentage,
            "level": level,
            "questions_answered": len(form.scores),
        }
    })

# ── API: visitor event ────────────────────────────────────────────────────────
@app.post("/api/event")
async def visitor_event(ev: VisitorEvent, request: Request):
    ip = request.client.host if request.client else "?"
    vid = request.cookies.get("o2_vid", str(uuid.uuid4()))
    _db_exec(VISITORS_DB,
        "INSERT INTO events(vid,ts,event_type,data,ip) VALUES(?,?,?,?,?)",
        (vid, datetime.datetime.utcnow().isoformat(), ev.event,
         json.dumps(ev.data or {}), ip))
    return JSONResponse({"ok": True})

# ── API: metrics ──────────────────────────────────────────────────────────────
@app.get("/api/metrics")
async def metrics():
    uptime_s = int(time.time() - COUNTERS["uptime_start"])
    try:
        con = sqlite3.connect(DB_PATH, check_same_thread=False)
        df_req = pd.read_sql_query(
            "SELECT ts,status,duration_ms FROM requests WHERE ts>=datetime('now','-24 hours')", con)
        df_leads = pd.read_sql_query(
            "SELECT ts,name,company,email,challenge,email_sent FROM leads ORDER BY ts DESC LIMIT 50", con)
        df_waf = pd.read_sql_query(
            "SELECT ts,ip,reason,action FROM waf_events ORDER BY ts DESC LIMIT 50", con)
        df_assess = pd.read_sql_query(
            "SELECT ts,name,company,email,area,total_score,percentage FROM assessments ORDER BY ts DESC LIMIT 20", con)
        con.close()
        req_stats = {}
        if not df_req.empty:
            df_req["duration_ms"] = pd.to_numeric(df_req["duration_ms"], errors="coerce")
            req_stats = {
                "count_24h": int(len(df_req)),
                "avg_ms": round(float(df_req["duration_ms"].mean()), 2),
                "p95_ms": round(float(np.percentile(df_req["duration_ms"].dropna(), 95)), 2),
                "status_2xx": int((df_req["status"] < 300).sum()),
                "status_4xx": int(((df_req["status"] >= 400) & (df_req["status"] < 500)).sum()),
                "status_5xx": int((df_req["status"] >= 500).sum()),
            }
        # Visitors stats
        con2 = sqlite3.connect(VISITORS_DB, check_same_thread=False)
        total_vis = con2.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        today_vis = con2.execute(
            "SELECT COUNT(*) FROM visitors WHERE last_seen>=date('now')").fetchone()[0]
        con2.close()
    except Exception as e:
        logger.error(f"metrics: {e}")
        req_stats={}; df_leads=pd.DataFrame(); df_waf=pd.DataFrame()
        df_assess=pd.DataFrame(); total_vis=0; today_vis=0

    return JSONResponse({
        "server": {"uptime_seconds": uptime_s, "port": PORT, "db": str(DB_PATH)},
        "counters": {k: v for k, v in COUNTERS.items() if k != "uptime_start"},
        "requests_24h": req_stats,
        "leads_recent": df_leads.to_dict("records") if not df_leads.empty else [],
        "waf_recent": df_waf.to_dict("records") if not df_waf.empty else [],
        "assessments_recent": df_assess.to_dict("records") if not df_assess.empty else [],
        "visitors": {"total": total_vis, "today": today_vis},
        "queues": {"events": _EVENT_QUEUE.qsize(), "email": _EMAIL_QUEUE.qsize()},
        "bans_active": len(_IP_BANS),
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
    })

@app.get("/api/health")
async def health():
    return {"status": "ok", "ts": datetime.datetime.utcnow().isoformat(), "version": "2.1.0"}

@app.get("/api/bans")
async def list_bans():
    con = sqlite3.connect(BANS_DB, check_same_thread=False)
    rows = con.execute("SELECT ip,reason,banned_at,unban_at,permanent,hit_count FROM ip_bans ORDER BY banned_at DESC LIMIT 100").fetchall()
    con.close()
    return JSONResponse([{"ip":r[0],"reason":r[1],"banned_at":r[2],"unban_at":r[3],"permanent":bool(r[4]),"hits":r[5]} for r in rows])

@app.delete("/api/bans/{ip}")
async def unban_ip(ip: str):
    if ip in _IP_BANS:
        del _IP_BANS[ip]
    _db_exec(BANS_DB, "DELETE FROM ip_bans WHERE ip=?", (ip,))
    clog(f"IP desbloqueado: {ip}", "success", "✅")
    return JSONResponse({"ok": True, "ip": ip})

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # ── Hot reload: monitora APENAS pastas de código ─────────────────────────
    # data/, logs/ e __pycache__ são EXCLUÍDAS para evitar reload em escrita
    # de .db, .log, visitors_log.yaml/.json/.md gerados em runtime.
    _watch_dirs = [
        str(d) for d in [
            BASE_DIR / "partials",
            BASE_DIR / "assets",
            BASE_DIR / "config",
        ] if d.exists()
    ]
    # Inclui a raiz para capturar mudanças no server.py
    _watch_dirs.append(str(BASE_DIR))

    # Pastas e padrões que NUNCA devem disparar reload
    # IMPORTANTE: reload_excludes só aceita padrões RELATIVOS (glob), não caminhos absolutos
    _exclude = [
        "data/*",
        "logs/*",
        "__pycache__/*",
        "*.db",
        "*.log",
        "*.pyc",
        "*.json",
        "visitors_log*",
        "o2_metrics*",
        "bans*",
    ]

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        reload_dirs=_watch_dirs,
        reload_includes=["*.py", "*.html", "*.css", "*.js", "*.yaml", "*.yml"],
        reload_excludes=_exclude,
        log_level="warning",
    )
