# pages.py - MX-UI v1.0.0
# Placeholders:
#   SUB_INFO_HTML : {label} {active ? ...} {used_fmt} {limit_fmt} {expires_at} {vless_link} {sub_url} {watermark}
#   SUB_USER_HTML : %%LABEL%% %%UUID%% %%QR_URL%% %%STATUS%% %%DOWNLOADED%% %%UPLOADED%% %%USAGE%% %%TOTAL_QUOTA%%
#                   %%REMAINED%% %%LAST_ONLINE%% %%EXPIRY%% %%IPS%% %%APPLIED_IPS_COUNT%% %%LINKS_LIST_HTML%%
#                   %%USED_FMT%% %%LIMIT_FMT%% %%USAGE_PCT%% %%VLESS_LINK%% %%WATERMARK%% %%STATUS_DOT%% %%STATUS_TEXT%%

BASE_CSS = """
:root{--bg:#f3f4f1;--surface:#fff;--sunk:#eceee9;--ink:#14181b;--mut:#657074;--line:#dfe2dc;--acc:#0b8f7e;--acc-ink:#fff;--acc-soft:rgba(11,143,126,.1);--bad:#cf4230;--bad-soft:rgba(207,66,48,.1);--warn:#b7791f;--warn-soft:rgba(183,121,31,.13);--c2:#3f6fd9;--c3:#c8871f;--r:14px;--ui:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace;color-scheme:light}
:root[data-theme=dark]{--bg:#0e1211;--surface:#161b19;--sunk:#0b0e0d;--ink:#eef1ee;--mut:#8e9995;--line:#252c29;--acc:#37cbb2;--acc-ink:#04201a;--acc-soft:rgba(55,203,178,.12);--bad:#ff7b67;--bad-soft:rgba(255,123,103,.13);--warn:#e0b25a;--warn-soft:rgba(224,178,90,.14);--c2:#7aa2ff;--c3:#e0b25a;color-scheme:dark}
*{box-sizing:border-box;margin:0}
html{-webkit-text-size-adjust:100%}
body{font-family:var(--ui);background:var(--bg);color:var(--ink);font-size:15px;line-height:1.5;min-height:100vh;min-height:100dvh;-webkit-font-smoothing:antialiased}
body.lock{overflow:hidden}
h1,h2,h3,h4{letter-spacing:-.02em;line-height:1.2}
button,input,select,textarea{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.mono{font-family:var(--mono)}.mut{color:var(--mut)}.hidden{display:none!important}
svg.i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.field{display:block;min-width:0}
.field>span{display:block;font-size:13px;font-weight:600;margin-bottom:6px}
.input{width:100%;height:46px;padding:0 14px;background:var(--surface);border:1px solid var(--line);border-radius:10px;transition:border-color .15s,box-shadow .15s}
select.input{padding-right:8px}
.input:focus{outline:none;border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.input[readonly],.input:disabled{background:var(--sunk);color:var(--mut)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:44px;padding:0 18px;border-radius:10px;border:1px solid var(--line);background:var(--surface);font-weight:600;font-size:14px;cursor:pointer;white-space:nowrap;transition:background .15s,border-color .15s,transform .1s,filter .15s}
.btn:hover{border-color:var(--mut)}.btn:active{transform:scale(.98)}.btn:disabled{opacity:.55;cursor:not-allowed}
.btn.primary{background:var(--acc);border-color:var(--acc);color:var(--acc-ink)}.btn.primary:hover{filter:brightness(1.07)}
.btn.danger{background:var(--bad);border-color:var(--bad);color:#fff}
.btn.sm{height:34px;padding:0 12px;font-size:13px}.btn.block{width:100%}
.alert{padding:10px 12px;border-radius:10px;background:var(--bad-soft);color:var(--bad);font-size:13px;font-weight:600}
.logo{width:34px;height:34px;border-radius:10px;background:var(--ink);color:var(--bg);display:grid;place-items:center;font-weight:800;font-size:13px;letter-spacing:-.04em;flex:none}
.pill{display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:99px;font-size:12px;font-weight:700;background:var(--sunk);color:var(--mut);white-space:nowrap}
.pill i{width:7px;height:7px;border-radius:50%;background:currentColor}
.pill.ok,.pill.active{background:var(--acc-soft);color:var(--acc)}.pill.off,.pill.inactive{background:var(--bad-soft);color:var(--bad)}
.toast{position:fixed;left:50%;bottom:calc(20px + env(safe-area-inset-bottom));transform:translate(-50%,16px);max-width:min(92vw,420px);background:var(--ink);color:var(--bg);padding:10px 16px;border-radius:10px;font-size:14px;font-weight:600;text-align:center;opacity:0;pointer-events:none;transition:opacity .22s,transform .22s;z-index:100}
.toast.on{opacity:1;transform:translate(-50%,0)}.toast.ok{background:var(--acc);color:var(--acc-ink)}.toast.err{background:var(--bad);color:#fff}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>try{var t=localStorage.getItem('mx-theme')}catch(e){}document.documentElement.dataset.theme=t||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light')</script>
__EXTRA__<style>__BASE__
__CSS__</style>
</head>
"""

def _page(title, css, body, extra=""):
    return (_HEAD.replace("__TITLE__", title).replace("__EXTRA__", extra)
            .replace("__BASE__", BASE_CSS).replace("__CSS__", css) + body)

_UTIL_JS = """
function toast(t,k){
  var e=document.getElementById('toast');
  if(!e)return;
  e.textContent=t;
  e.className='toast on '+(k||'');
  clearTimeout(toast.t);
  toast.t=setTimeout(function(){e.classList.remove('on');},2400);
}
function copyText(t){
  var ok=function(){toast('Copied to clipboard','ok');};
  var fb=function(){
    var a=document.createElement('textarea');
    a.value=t;
    a.style.cssText='position:fixed;opacity:0;left:-9999px';
    document.body.appendChild(a);
    a.select();
    try{document.execCommand('copy');ok();}catch(e){toast('Copy failed','err');}
    a.remove();
  };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(ok,fb);
  } else {
    fb();
  }
}
function cp(id,b){
  var el=document.getElementById(id);
  if(!el)return;
  copyText(el.value);
  var t=b.textContent;
  if(t.trim()){
    b.textContent='Copied';
    setTimeout(function(){b.textContent=t;},1200);
  }
}
"""

_AUTH_CSS = """
.auth{min-height:100vh;min-height:100dvh;display:grid;grid-template-columns:1.05fr 1fr}
.side{background:var(--ink);color:var(--bg);padding:40px 48px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.side .logo{background:var(--bg);color:var(--ink)}
.side h2{font-size:clamp(30px,3.6vw,46px);max-width:13ch;font-weight:800}
.side p{opacity:.65;max-width:34ch;margin-top:14px}.side small{opacity:.5;font-size:13px}
.side .rings{position:absolute;right:-140px;bottom:-140px;width:420px;height:420px;border-radius:50%;border:1px solid rgba(255,255,255,.14);box-shadow:0 0 0 60px rgba(255,255,255,.03),0 0 0 120px rgba(255,255,255,.025)}
.main{display:grid;place-items:center;padding:32px 24px}
.form{width:100%;max-width:380px;display:grid;gap:18px}
.form h1{font-size:28px;font-weight:800}
.hint{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;border:1px dashed var(--line);border-radius:10px;font-size:13px;color:var(--mut)}
.hint button{border:0;background:var(--acc-soft);color:var(--acc);font:600 13px var(--mono);padding:5px 10px;border-radius:7px;cursor:pointer}
.ok-msg{padding:10px 12px;border-radius:10px;background:var(--acc-soft);color:var(--acc);font-size:13px;font-weight:600}
.shake{animation:shake .35s}.shake{border-color:var(--bad)!important}
@keyframes shake{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
.foot{text-align:center;font-size:12px;color:var(--mut)}
@media(max-width:820px){.auth{grid-template-columns:1fr;grid-template-rows:auto 1fr}.side{padding:20px 24px;flex-direction:row;align-items:center}.side h2,.side p,.side small,.rings{display:none}}
"""
_SIDE = """<aside class="side"><div class="logo">MX</div><div><h2>Your nodes, under one roof.</h2><p>Create VLESS-WS configs, track traffic and share subscriptions.</p></div><small>MX-UI v1.0.0</small><div class="rings"></div></aside>"""

LOGIN_HTML = _page("Login · MX-UI", _AUTH_CSS, """<body>
<div class="auth">""" + _SIDE + """
<main class="main">
<form id="loginForm" class="form">
  <div><h1>Sign in</h1><p class="mut" style="margin-top:6px">Enter the admin password to open the dashboard.</p></div>
  <div class="hint" id="hint"><span>Default password</span><button type="button" id="default-password-display" onclick="fillPw()">MUVIXO</button></div>
  <label class="field"><span>Password</span><input type="password" id="pw" class="input" required autofocus autocomplete="current-password" placeholder="Enter password"></label>
  <button type="submit" id="loginButton" class="btn primary block">Sign in</button>
  <div id="errorMsg" class="alert hidden" role="alert"></div>
  <p class="foot">Created by Muvixo</p>
</form>
</main></div>
<script>
var $=function(id){return document.getElementById(id);};
function fillPw(){var p=$('pw');p.value='MUVIXO';p.focus();}
async function checkDefaultPassword(){
  try{
    var r=await fetch('/api/is-default-password');
    var d=await r.json();
    if(!d.is_default)$('hint').innerHTML='<span>Use your custom password.</span>';
  }catch(e){}
}
checkDefaultPassword();
addEventListener('pageshow',function(e){if(e.persisted)checkDefaultPassword();});
$('loginForm').onsubmit=async function(e){
  e.preventDefault();
  var btn=$('loginButton'),err=$('errorMsg'),pw=$('pw');
  err.classList.add('hidden');btn.disabled=true;btn.textContent='Signing in...';
  try{
    var res=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw.value})});
    if(!res.ok){
      var m='Wrong password. Check it and try again.';
      try{var d=await res.json();if(d&&d.detail)m=d.detail;}catch(x){}
      throw new Error(m);
    }
    location.href='/dashboard';
  }catch(x){
    err.textContent=x.message;err.classList.remove('hidden');btn.disabled=false;btn.textContent='Sign in';
    pw.classList.remove('shake');void pw.offsetWidth;pw.classList.add('shake');pw.value='';pw.focus();
  }
};
</script>
</body>
</html>""")

SETUP_HTML = _page("Initial Setup · MX-UI", _AUTH_CSS, """<body>
<div class="auth">""" + _SIDE + """
<main class="main">
<form id="setupForm" class="form">
  <div><h1>Set admin password</h1><p class="mut" style="margin-top:6px">First run. Choose a password to secure your dashboard.</p></div>
  <label class="field"><span>New password</span><input type="password" id="setup-pw" class="input" required minlength="4" autofocus autocomplete="new-password" placeholder="At least 4 characters"></label>
  <label class="field"><span>Confirm password</span><input type="password" id="setup-pw-confirm" class="input" required minlength="4" autocomplete="new-password" placeholder="Repeat password"></label>
  <button type="submit" id="setupButton" class="btn primary block">Save and continue</button>
  <div id="setupErrorMsg" class="alert hidden" role="alert"></div>
  <div id="setupSuccessMsg" class="ok-msg hidden" role="status"></div>
  <p class="foot">Created by Muvixo</p>
</form>
</main></div>
<script>
var $=function(id){return document.getElementById(id);};
$('setupForm').onsubmit=async function(e){
  e.preventDefault();
  var btn=$('setupButton'),err=$('setupErrorMsg'),ok=$('setupSuccessMsg');
  err.classList.add('hidden');ok.classList.add('hidden');
  var pw=$('setup-pw').value,c=$('setup-pw-confirm').value;
  var fail=function(m){err.textContent=m;err.classList.remove('hidden');};
  if(pw.length<4)return fail('Password must be at least 4 characters.');
  if(pw!==c)return fail("Passwords do not match.");
  btn.disabled=true;btn.textContent='Saving...';
  try{
    var res=await fetch('/api/setup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw})});
    var d=await res.json().catch(function(){return {};});
    if(!res.ok)throw new Error(d.detail||'Setup failed. Try again.');
    ok.textContent='Setup complete. Redirecting...';ok.classList.remove('hidden');
    setTimeout(function(){location.href='/login';},1200);
  }catch(x){fail(x.message);btn.disabled=false;btn.textContent='Save and continue';}
};
</script>
</body>
</html>""")

_SUB_CSS = """
body{display:grid;place-items:center;padding:20px}
.card{width:100%;max-width:520px;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:28px;display:grid;gap:20px}
.top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.top h1{font-size:24px;font-weight:800;word-break:break-word}
.meter{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.meter div{padding:14px 16px;min-width:0}.meter div+div{border-left:1px solid var(--line)}
.meter small{display:block;color:var(--mut);font-size:12px;font-weight:600}.meter b{font-size:16px;font-weight:800;word-break:break-word}
.copy{display:grid;gap:6px}.copy>span{font-size:13px;font-weight:600}.copy>div{display:flex;gap:8px}
.copy .input{font:13px var(--mono);height:44px;min-width:0}
.foot{text-align:center;font-size:12px;color:var(--mut)}
@media(max-width:480px){.card{padding:20px;border-radius:18px}.meter{grid-template-columns:1fr}.meter div+div{border-left:0;border-top:1px solid var(--line)}}
"""

SUB_INFO_HTML = _page("Subscription Info · MX-UI", _SUB_CSS, """<body>
<main class="card">
  <div class="top">
    <div><h1>{label}</h1><p class="mut" style="font-size:13px;margin-top:2px">Subscription info</p></div>
    <span class="pill {active ? 'active' : 'inactive'}"><i></i>{active ? 'Active' : 'Inactive'}</span>
  </div>
  <div class="meter">
    <div><small>Usage</small><b class="mono">{used_fmt} / {limit_fmt}</b></div>
    <div><small>Expires</small><b class="mono">{expires_at}</b></div>
  </div>
  <div class="copy"><span>Configuration link</span><div><input id="u1" readonly class="input" value="{vless_link}"><button class="btn primary" onclick="cp('u1',this)">Copy</button></div></div>
  <div class="copy"><span>Subscription URL</span><div><input id="u2" readonly class="input" value="{sub_url}"><button class="btn" onclick="cp('u2',this)">Copy</button></div></div>
  <p class="foot">{watermark}</p>
</main>
<div id="toast" class="toast" role="status"></div>
<script>""" + _UTIL_JS + """</script>
</body>
</html>""")

_PORTAL_CSS = """
body{padding:20px 14px}
.wrap{max-width:640px;margin:0 auto}
.card{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:26px;display:grid;gap:22px}
.bar1{display:flex;align-items:center;gap:10px}.bar1 .sp{flex:1;min-width:0;font-weight:800}.bar1 small{display:block;color:var(--mut);font-weight:600;font-size:12px}
.title{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.title h2{font-size:26px;font-weight:800;word-break:break-word}
.qr{justify-self:center;background:#fff;padding:12px;border-radius:16px;border:1px solid var(--line);width:min(210px,64vw);aspect-ratio:1}
.qr img{width:100%;height:100%;object-fit:contain;display:block}
.rows>div{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:10px 2px;border-bottom:1px solid var(--line);font-size:14px}
.rows>div:last-child{border:0}.rows span:first-child{color:var(--mut);font-weight:600;font-size:13px;flex:none}
.rows span:last-child{font-family:var(--mono);text-align:right;word-break:break-all;min-width:0}
.sec-h{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}.sec-h b{font-size:14px}
.tag{font:600 11px var(--mono);padding:2px 9px;border-radius:99px;background:var(--acc-soft);color:var(--acc)}
#linksContainer{background:#0c1112;color:#e2e8f0;border-radius:12px;overflow:hidden;border:1px solid var(--line)}
.link-row{display:flex;align-items:center;gap:10px;padding:10px 12px;border-bottom:1px solid rgba(255,255,255,.07);cursor:pointer;transition:background .15s;min-width:0}
.link-row:last-child{border:0}.link-row:hover{background:rgba(255,255,255,.05)}
.link-row input[type=text]{flex:1;min-width:0;background:transparent;border:0;color:#9aa8ae;font:12px var(--mono);outline:none;text-overflow:ellipsis}
.link-tag{font:600 10px var(--mono);padding:1px 7px;border-radius:99px;background:rgba(55,203,178,.14);color:#37cbb2;white-space:nowrap}
.prog{padding:16px;background:var(--sunk);border-radius:12px}
.prog .t{display:flex;justify-content:space-between;gap:10px;font-size:13px;flex-wrap:wrap}.prog .t span:last-child{font-family:var(--mono);color:var(--mut)}
.track{height:8px;background:var(--line);border-radius:8px;overflow:hidden;margin:10px 0 6px}.track i{display:block;height:100%;background:var(--acc);border-radius:8px;transition:width .8s}
.prog .b{display:flex;justify-content:space-between;font-size:12px;color:var(--mut);gap:8px}
.copy{display:flex;gap:8px}.copy .input{font:12px var(--mono);height:44px;min-width:0}
.mark{text-align:center;font-size:12px;color:var(--mut);margin-top:10px}
@media(max-width:520px){.card{padding:18px;border-radius:18px}.title h2{font-size:22px}.copy{flex-direction:column}.copy .btn{width:100%}}
"""

_ROWS = [("Label", "labelValue", "%%LABEL%%"), ("Subscription ID", "uuidValue", "%%UUID%%"), ("Status", "statusValue", "%%STATUS%%"),
         ("Downloaded", "downloadedValue", "%%DOWNLOADED%%"), ("Uploaded", "uploadedValue", "%%UPLOADED%%"),
         ("Usage", "usageValue", "%%USAGE%% / %%TOTAL_QUOTA%%"), ("Total quota", "totalQuotaValue", "%%TOTAL_QUOTA%%"),
         ("Remaining", "remainedValue", "%%REMAINED%%"), ("Last online", "lastOnlineValue", "%%LAST_ONLINE%%"),
         ("Expiry", "expiryValue", "%%EXPIRY%%"), ("IPs connected", "ipsValue", "%%IPS%%")]
_ROWS_HTML = "".join('<div><span>%s</span><span id="%s">%s</span></div>' % r for r in _ROWS)

SUB_USER_HTML = _page("Subscription · MX-UI", _PORTAL_CSS, """<body>
<div class="wrap"><div class="card" id="card">
  <div class="bar1"><div class="logo">MX</div><div class="sp">MX-UI<small>v1.0.0</small></div></div>
  <div class="title"><h2 id="labelDisplay">%%LABEL%%</h2><span class="pill %%STATUS_DOT%%"><i></i>%%STATUS_TEXT%%</span></div>
  <div class="qr"><img id="qrImage" src="%%QR_URL%%" alt="Subscription QR code"></div>
  <div class="rows" id="detailsGrid">""" + _ROWS_HTML + """</div>
  <div>
    <div class="sec-h"><b>Connection links</b><span style="display:flex;gap:8px;align-items:center"><span class="tag">%%APPLIED_IPS_COUNT%% IP variant(s)</span><button class="btn sm" id="copyAllBtn" onclick="copyAllLinks()">Copy all</button></span></div>
    <div id="linksContainer">%%LINKS_LIST_HTML%%</div>
  </div>
  <div class="prog">
    <div class="t"><span id="progressLabel">%%LABEL%%</span><span id="progressText">%%USED_FMT%% / %%LIMIT_FMT%%</span></div>
    <div class="track"><i id="progressBar" style="width: %%USAGE_PCT%%%;"></i></div>
    <div class="b"><span id="usagePercent">%%USAGE_PCT%%% used</span><span id="remainedText">%%REMAINED%% remaining</span></div>
  </div>
  <div class="copy"><input type="text" readonly value="%%VLESS_LINK%%" id="vless-link-input" class="input" aria-label="VLESS link"><button class="btn primary" onclick="cp('vless-link-input',this)">Copy link</button></div>
  <p class="mark">%%WATERMARK%%</p>
</div></div>
<div id="toast" class="toast" role="status"></div>
<script>""" + _UTIL_JS + """
var $=function(id){return document.getElementById(id);};
function copyAllLinks(){
  var inputs=document.querySelectorAll('.link-row input[type="text"]');
  var v=[];
  for(var i=0;i<inputs.length;i++){
    if(inputs[i].value)v.push(inputs[i].value);
  }
  if(!v.length)return toast('No links to copy','err');
  copyText(v.join('\\n'));
  var b=$('copyAllBtn');
  if(b){
    b.textContent='Copied';
    setTimeout(function(){b.textContent='Copy all';},1800);
  }
}
var lc=$('linksContainer');
if(lc){
  lc.addEventListener('click',function(e){
    if(e.target.closest('.copy-btn'))return;
    var row=e.target.closest('.link-row');
    if(!row)return;
    var inp=row.querySelector('input[type="text"]');
    if(inp)copyText(inp.value);
  });
}
</script>
</body>
</html>""", extra='<script src="https://cdn.tailwindcss.com"></script><script>tailwind.config={corePlugins:{preflight:false}}</script>\n')

_DASH_CSS = """
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top)}
header .wrap{height:64px;display:flex;align-items:center;justify-content:space-between;gap:10px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px;letter-spacing:-.02em;min-width:0}
.brand small{font-size:11px;font-weight:600;color:var(--mut);display:block;line-height:1}
.tools{display:flex;align-items:center;gap:2px}
.ib{width:40px;height:40px;display:grid;place-items:center;border-radius:10px;border:1px solid transparent;background:transparent;color:var(--mut);cursor:pointer;transition:background .15s,color .15s}
.ib:hover{background:var(--sunk);color:var(--ink)}
.ib.sm{width:34px;height:34px;border-color:var(--line);background:var(--surface);flex:none}
.ib.danger:hover{background:var(--bad-soft);color:var(--bad);border-color:transparent}
main{padding:24px 0 36px;display:grid;gap:24px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--r)}
.stats,.rings{display:grid;grid-template-columns:repeat(4,1fr)}
.stat{padding:16px 20px;min-width:0}.stat+.stat,.ring+.ring{border-left:1px solid var(--line)}
.stat small{display:block;color:var(--mut);font-size:13px;font-weight:600}
.stat b{display:block;font-size:24px;font-weight:800;letter-spacing:-.03em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sec-h{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.sec-h h2{font-size:18px;font-weight:800}.sec-r{display:flex;gap:8px;align-items:center}
.link-btn{background:none;border:0;color:var(--acc);font-weight:700;font-size:13px;cursor:pointer;display:inline-flex;align-items:center;gap:4px;padding:6px 4px}
.link-btn svg{transition:transform .3s}.link-btn[aria-expanded=true] svg{transform:rotate(180deg)}
.ring{display:flex;align-items:center;gap:14px;padding:16px 20px;min-width:0}
.ring svg{width:54px;height:54px;flex:none;transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:4.5;stroke-linecap:round}.ring .bg{stroke:var(--sunk)}.ring .fg{transition:stroke-dasharray .6s}
.ring div{min-width:0}.ring small{display:block;color:var(--mut);font-size:13px;font-weight:600}
.ring b{display:block;font-size:19px;letter-spacing:-.02em;line-height:1.2}
.ring span{font-size:12px;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.exp{display:grid;grid-template-rows:0fr;transition:grid-template-rows .35s ease}.exp.open{grid-template-rows:1fr}.exp>div{overflow:hidden;min-height:0}
.dg{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding-top:12px}
.dc{padding:14px 16px;min-width:0}.dc h4{font-size:14px;margin-bottom:6px;display:flex;align-items:center;gap:8px}.dc h4 i{width:8px;height:8px;border-radius:50%;background:var(--c)}
.kv{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-top:1px solid var(--line);font-size:13px}
.kv span:first-child{color:var(--mut)}.kv span:last-child{font-family:var(--mono);text-align:right;word-break:break-all}
.search{width:240px;height:40px}
.list{overflow:hidden}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px 24px;align-items:center;padding:18px 20px}
.row+.row{border-top:1px solid var(--line)}.row:hover{background:color-mix(in srgb,var(--sunk) 50%,transparent)}
.row.def{box-shadow:inset 3px 0 var(--warn)}
.name{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.name b{font-size:16px;word-break:break-word}
.tag{font:600 11px var(--mono);color:var(--mut);border:1px solid var(--line);padding:1px 7px;border-radius:6px;white-space:nowrap}
.tag.acc{color:var(--acc);border-color:transparent;background:var(--acc-soft)}.tag.warn{color:var(--warn);border-color:transparent;background:var(--warn-soft)}
.meta{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:12px;color:var(--mut);margin-top:8px}.meta b{color:var(--ink);font-weight:600;font-family:var(--mono)}
.bar{height:5px;background:var(--sunk);border-radius:5px;margin-top:10px;max-width:340px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--acc);transition:width .5s}.bar.warn i{background:var(--c3)}.bar.full i{background:var(--bad)}
.ctl{display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.lk{display:flex;align-items:center;gap:6px;width:230px}.lk .input{height:34px;font:11px var(--mono);padding:0 10px}
.sw{position:relative;display:inline-flex;align-items:center;gap:8px;cursor:pointer;font-size:12px;font-weight:600;color:var(--mut)}
.sw input{position:absolute;opacity:0;width:0;height:0}.sw em{font-style:normal;min-width:54px}
.sw i{width:36px;height:20px;border-radius:20px;background:var(--line);position:relative;transition:background .2s}
.sw i::after{content:'';position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:#fff;transition:transform .2s}
.sw input:checked+i{background:var(--acc)}.sw input:checked+i::after{transform:translateX(16px)}
.sw input:focus-visible+i{outline:2px solid var(--acc);outline-offset:2px}.sw input:disabled+i{opacity:.5}
.empty{padding:48px 20px;text-align:center;color:var(--mut)}.empty b{display:block;color:var(--ink);font-size:17px;margin-bottom:4px}
.dfoot{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:18px 20px calc(18px + env(safe-area-inset-bottom));border-top:1px solid var(--line);font-size:12px;color:var(--mut)}
.modal{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(6,9,8,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .22s ease,visibility 0s linear .22s}
.modal.top{z-index:80}
.modal.open{opacity:1;visibility:visible;pointer-events:auto;transition:opacity .22s ease,visibility 0s}
.sheet{position:relative;width:100%;max-width:var(--w,480px);max-height:calc(100vh - 32px);max-height:calc(100dvh - 32px);display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:20px;box-shadow:0 30px 80px rgba(0,0,0,.3);outline:none;transform:translateY(16px) scale(.97);opacity:0;transition:transform .28s cubic-bezier(.2,.8,.2,1),opacity .22s ease}
.modal.open .sheet{transform:none;opacity:1}
.mh{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:20px 22px 0;flex:none}
.mh h3{font-size:19px;font-weight:800}.mh p{color:var(--mut);font-size:13px;margin-top:3px}
.mb{flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:16px 22px 22px;display:grid;gap:16px;align-content:start}
.mb>*{min-width:0}
.mf{flex:none;display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;padding:14px 22px;border-top:1px solid var(--line)}
.cen{padding:26px 22px 22px;display:grid;gap:14px;justify-items:center;text-align:center}.cen p{color:var(--mut);font-size:14px}.cen .row2{display:flex;gap:10px;width:100%}.cen .row2 .btn{flex:1}
.bdg{width:48px;height:48px;border-radius:50%;display:grid;place-items:center;background:var(--bad-soft);color:var(--bad)}.bdg.info{background:var(--acc-soft);color:var(--acc)}.bdg svg{width:22px;height:22px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.inline{display:flex;gap:8px}.inline .input{flex:1}.inline select.input{flex:none;width:96px}
.sub{font-size:12px;font-weight:700;color:var(--mut)}
.box{border:1px solid var(--line);border-radius:12px;padding:6px;max-height:190px;overflow:auto;background:var(--sunk)}
.box.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:8px}
.chk{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:500;min-width:0;word-break:break-all}
.chk:hover{background:var(--surface)}.chk input{accent-color:var(--acc);width:16px;height:16px;flex:none}.chk .tag{margin-left:auto}
.note{display:flex;gap:12px;padding:12px 14px;border-radius:12px;font-size:13px}.note svg{margin-top:2px}
.note.ok{background:var(--acc-soft);color:var(--acc)}.note.warn{background:var(--warn-soft);color:var(--warn)}.note b{display:block}.note p{color:var(--mut);margin-top:2px}
.c2{border:1px solid var(--line);border-radius:12px;padding:14px;display:grid;gap:10px;align-content:start}
.mini{padding:12px 14px;border:1px solid var(--line);border-radius:12px;min-width:0}.mini small{display:block;color:var(--mut);font-size:12px;font-weight:600}.mini b{font:600 15px var(--mono);word-break:break-all}
.tw{overflow-x:auto}.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{text-align:left;color:var(--mut);font-weight:600;padding:8px;border-bottom:1px solid var(--line);white-space:nowrap}.tbl td{padding:8px;border-bottom:1px solid var(--line);white-space:nowrap}.tbl .r{text-align:right}
.tbl .good{color:var(--acc)}.tbl .bad{color:var(--bad)}
.qrs{display:grid;grid-template-columns:1fr 1fr;gap:14px}.qrc{text-align:center;display:grid;gap:8px;justify-items:center;align-content:start}
.qb{background:#fff;padding:10px;border-radius:14px;border:1px solid var(--line);width:min(170px,100%);aspect-ratio:1}.qb img{width:100%;height:100%;object-fit:contain;display:block}
.qrc p{font-size:11px;word-break:break-all;color:var(--mut);max-height:54px;overflow:auto}
@media(max-width:1020px){.row{grid-template-columns:1fr}.ctl{justify-content:flex-start}.lk{flex:1;min-width:190px;width:auto}}
@media(max-width:860px){
 .stats,.rings{grid-template-columns:1fr 1fr}.stat:nth-child(3),.ring:nth-child(3){border-left:0}.stat:nth-child(n+3),.ring:nth-child(n+3){border-top:1px solid var(--line)}
 .dg{grid-template-columns:1fr 1fr}.g4{grid-template-columns:1fr 1fr}
}
@media(max-width:600px){
 .wrap{padding:0 14px}.hide-m{display:none}.stat,.ring{padding:14px 16px}.stat b{font-size:20px}.ring b{font-size:17px}.ring svg{width:46px;height:46px}
 .ib{width:36px;height:36px}.sec-r{width:100%}.search{flex:1;width:auto}.dg,.g2,.qrs{grid-template-columns:1fr}.box.grid{grid-template-columns:1fr 1fr}
 .row{padding:16px 14px}.lk{min-width:100%}.dfoot{flex-direction:column}
 .modal{align-items:flex-end;padding:0}
 .sheet{max-width:none;border-radius:20px 20px 0 0;border-bottom:0;max-height:92vh;max-height:92dvh;transform:translateY(100%);opacity:1}
 .modal.open .sheet{transform:none}
 .mh{padding:18px 18px 0}.mb{padding:14px 18px 18px}.mf{padding:12px 18px calc(12px + env(safe-area-inset-bottom))}.mf .btn{flex:1}
 .modal.top{align-items:center;padding:16px}
 .modal.top .sheet{border-radius:20px;border-bottom:1px solid var(--line);transform:translateY(16px) scale(.97);opacity:0}
 .modal.top.open .sheet{transform:none;opacity:1}
}
@media(max-width:380px){.tools .ib:nth-child(3){display:none}}
"""

_SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + "".join(
    '<symbol id="%s" viewBox="0 0 24 24">%s</symbol>' % kv for kv in {
        "plus": '<path d="M12 5v14M5 12h14"/>',
        "x": '<path d="M18 6 6 18M6 6l12 12"/>',
        "copy": '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
        "qr": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3M21 14v.01M14 21h3M21 17v4"/>',
        "open": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
        "edit": '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
        "trash": '<path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6"/>',
        "reset": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
        "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
        "pulse": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
        "db": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
        "cog": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/>',
        "out": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
        "theme": '<circle cx="12" cy="12" r="9"/><path d="M12 3v18a9 9 0 0 0 0-18Z" fill="currentColor"/>',
        "refresh": '<path d="M21 12a9 9 0 0 0-15-6.7L3 8M3 3v5h5M3 12a9 9 0 0 0 15 6.7L21 16M21 21v-5h-5"/>',
        "dl": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
        "up": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
        "chev": '<path d="m6 9 6 6 6-6"/>',
        "check": '<path d="M20 6 9 17l-5-5"/>',
        "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/>',
        "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
        "play": '<path d="m6 3 14 9-14 9Z"/>',
        "ok": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
        "terminal": '<path d="m4 17 6-6-6-6M12 19h8"/>',
    }.items()) + '</defs></svg>'

def _ic(n, c="i"):
    return '<svg class="%s"><use href="#%s"/></svg>' % (c, n)

def _ib(on, icon, title, extra=""):
    return '<button class="ib %s" onclick="%s" title="%s" aria-label="%s">%s</button>' % (extra, on, title, title, _ic(icon))

_TOOLS = (_ib("location.href='/logs'", "terminal", "Logs")
          + _ib("toggleModal('ipSuggestModal',true)", "list", "IP suggestions")
          + _ib("toggleModal('healthModal',true)", "pulse", "Health check")
          + _ib("toggleModal('databaseModal',true)", "db", "Database")
          + _ib("toggleModal('settingsModal',true)", "cog", "Settings")
          + _ib("toggleTheme()", "theme", "Toggle theme")
          + _ib("goLogin()", "out", "Log out", "danger"))

def _modal(mid, title, sub, body, foot="", w=480):
    return ('<div id="%s" class="modal" role="dialog" aria-modal="true" aria-labelledby="%s-t"><div class="sheet" tabindex="-1" style="--w:%dpx">'
            '<div class="mh"><div><h3 id="%s-t">%s</h3>%s</div>%s</div><div class="mb">%s</div>%s</div></div>'
            % (mid, mid, w, mid, title, ('<p>%s</p>' % sub) if sub else "",
               _ib("toggleModal('%s',false)" % mid, "x", "Close", "sm"), body, ('<div class="mf">%s</div>' % foot) if foot else ""))

def _fld(label, ctl):
    return '<label class="field"><span>%s</span>%s</label>' % (label, ctl)

_FPS = ["chrome", "ios", "firefox", "safari", "android", "edge", "360", "qq", "random", "randomized"]

def _cfg(p):
    i = lambda k, t="text", x="": '<input id="%s-%s" type="%s" class="input" %s>' % (p, k, t, x)
    fp = "".join('<option value="%s">%s</option>' % (f, f) for f in _FPS)
    proto = ('<select id="%s-protocol" class="input"><option value="vless-ws">VLESS + WS</option></select>' % p)
    speed = ('<div class="inline">' + i("speed", "number", 'value="0" min="0" step="0.5" inputmode="decimal"')
             + '<select id="%s-speed-unit" class="input"><option value="MBIT">Mbps</option><option value="KB">KB/s</option><option value="MB">MB/s</option></select></div>' % p)
    return ('<div class="g2">' + _fld("Name", i("label", "text", 'placeholder="e.g. US-Reality" autocomplete="off"')) + _fld("Protocol", proto) + '</div>'
            '<div class="g2">' + _fld("Fingerprint (uTLS)", '<select id="%s-fp" class="input">%s</select>' % (p, fp))
            + _fld("ALPN (optional)", i("alpn", "text", 'placeholder="h2,http/1.1" autocomplete="off"')) + '</div>'
            '<div class="g2">' + _fld("Traffic limit (MB, 0 = unlimited)", i("limit", "number", 'value="0" min="0" step="any" inputmode="decimal"'))
            + _fld("Expiry (days, 0 = never)", i("expiry", "number", 'value="0" min="0" inputmode="numeric"')) + '</div>'
            '<div class="g2">' + _fld("IP limit (0 = unlimited)", i("iplimit", "number", 'value="0" min="0" inputmode="numeric"'))
            + _fld("Speed limit (0 = unlimited)", speed) + '</div>'
            '<div class="g2">' + _fld("Note (optional)", i("note", "text", 'placeholder="Internal remarks" autocomplete="off"')) + '</div>')

def _cfg_edit(p):
    i = lambda k, t="text", x="": '<input id="%s-%s" type="%s" class="input" %s>' % (p, k, t, x)
    fp = "".join('<option value="%s">%s</option>' % (f, f) for f in _FPS)
    proto = ('<select id="%s-protocol" class="input"><option value="vless-ws">VLESS + WS</option></select>' % p)
    return ('<div class="g2">' + _fld("Name", i("label", "text", 'placeholder="e.g. US-Reality" autocomplete="off"')) + _fld("Protocol", proto) + '</div>'
            '<div class="g2">' + _fld("Fingerprint (uTLS)", '<select id="%s-fp" class="input">%s</select>' % (p, fp))
            + _fld("ALPN (optional)", i("alpn", "text", 'placeholder="h2,http/1.1" autocomplete="off"')) + '</div>'
            '<div class="note warn" style="margin-top:12px"><div><b>Live Updates</b><p>Limits and notes are fixed once generated.</p></div></div>')

_DETAILS = [
    ("CPU", "--acc", [("Load average", "cpu-load-avg"), ("Cores", "cpu-cores-detail"), ("Usage (user)", "cpu-user"), ("Usage (system)", "cpu-system"), ("Usage (idle)", "cpu-idle")]),
    ("RAM", "--c2", [("Total", "ram-total-detail"), ("Used", "ram-used-detail"), ("Free", "ram-free-detail"), ("Available", "ram-available-detail"), ("Cached", "ram-cached-detail")]),
    ("Swap", "--c3", [("Total", "swap-total-detail"), ("Used", "swap-used-detail"), ("Free", "swap-free-detail"), ("Usage", "swap-usage-detail")]),
    ("Storage", "--bad", [("Total", "disk-total-detail"), ("Used", "disk-used-detail"), ("Free", "disk-free-detail"), ("Usage", "disk-usage-detail")]),
    ("Network", "--c2", [("Total traffic", "network-total"), ("Total requests", "network-requests"), ("Active connections", "network-connections"), ("Errors", "network-errors")]),
    ("System", "--acc", [("Uptime", "sys-uptime"), ("Active configs", "sys-active-configs"), ("Total configs", "sys-total-configs"), ("Expired configs", "sys-expired-configs")]),
]
_DETAILS_HTML = "".join(
    '<div class="panel dc" style="--c:var(%s)"><h4><i></i>%s</h4>%s</div>' % (c, n, "".join('<div class="kv"><span>%s</span><span id="%s">--</span></div>' % r for r in rows))
    for n, c, rows in _DETAILS)
_RINGS_HTML = "".join(
    '<div class="ring"><svg viewBox="0 0 40 40"><circle class="bg" cx="20" cy="20" r="16"/><circle id="ring-%s" class="fg" cx="20" cy="20" r="16" pathLength="100" stroke-dasharray="0 100" style="stroke:var(%s)"/></svg>'
    '<div><small>%s</small><b id="ring-%s-pct">0%%</b><span id="ring-%s-val" class="mut">--</span></div></div>' % (k, c, n, k, k)
    for k, c, n in [("cpu", "--acc", "CPU"), ("ram", "--c2", "RAM"), ("swap", "--c3", "Swap"), ("disk", "--bad", "Storage")])

_MODALS = "".join([
    _modal("inboundModal", "Add config", "Deploy a new VLESS-WS configuration.", _cfg("new"),
           '<button class="btn" onclick="toggleModal(\'inboundModal\',false)">Cancel</button><button class="btn primary" onclick="createConfig()">Deploy config</button>', 620),
    _modal("editModal", 'Edit <span id="editNodeTitle" style="color:var(--acc)">config</span>', "Live changes will immediately affect client configs.",
           '<input type="hidden" id="edit-uuid">' + _cfg_edit("edit"),
           '<button class="btn" onclick="toggleModal(\'editModal\',false)">Discard</button><button class="btn primary" onclick="saveEdit()">Save changes</button>', 620),
    _modal("ipSuggestModal", "IP suggestions", "Pick random IPs from a curated list. No pings, no bans.",
           '<div id="domainStatus" class="note warn"></div><div id="ipBody" class="mb" style="padding:0;overflow:visible">'
           '<div style="display:flex;justify-content:space-between;align-items:center"><span class="sub">Suggested IPs</span>'
           '<button class="btn sm" onclick="fetchSuggestions()">' + _ic("refresh") + 'Refresh</button></div>'
           '<div id="suggestList" class="box grid mono"><p class="mut" style="grid-column:1/-1;text-align:center;font-size:13px">Load IPs to get a fresh batch.</p></div>'
           '<div class="c2"><span class="sub">Apply to</span><div id="applyTargetList" class="box"></div>'
           '<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><span id="applyStatus" class="mut" style="font-size:12px">Load suggestions first</span>'
           '<button class="btn primary sm" id="applySuggestBtn" onclick="applySuggestedIPs()" disabled>' + _ic("check") + 'Apply to selected</button></div></div></div>',
           '<button class="btn" id="loadIpsBtn" onclick="fetchSuggestions()">' + _ic("refresh") + 'Load IPs</button><button class="btn" onclick="toggleModal(\'ipSuggestModal\',false)">Close</button>', 720),
    _modal("healthModal", "Config health check", "Test reachability of selected configs.",
           '<div id="healthConfigList" class="box"></div><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">'
           '<button class="btn primary" id="healthTestBtn" onclick="testSelectedConfigs()" disabled>' + _ic("play") + 'Test selected</button>'
           '<span id="healthStatus" class="mut" style="font-size:12px">Select configs to test</span></div><div id="healthResults"></div>',
           '<button class="btn" onclick="toggleModal(\'healthModal\',false)">Close</button>', 720),
    _modal("databaseModal", "Database", "View stored data and back up your configuration.",
           '<div class="g4"><div class="mini"><small>Total configs</small><b id="db-total-configs">0</b></div><div class="mini"><small>Active configs</small><b id="db-active-configs" style="color:var(--acc)">0</b></div>'
           '<div class="mini"><small>Total traffic</small><b id="db-total-traffic">0 B</b></div><div class="mini"><small>Last loaded</small><b id="db-last-saved" style="font-size:12px">Never</b></div></div>'
           '<div class="c2"><span class="sub">All configurations</span><div class="tw"><table class="tbl"><thead><tr><th>Label</th><th>UUID</th><th class="r">Used</th><th class="r">Limit</th><th>Status</th><th class="r">IPs</th></tr></thead><tbody id="dbConfigsBody"></tbody></table></div></div>'
           '<div class="c2"><span class="sub">Backup</span><p class="mut" style="font-size:13px">Download the complete database as JSON.</p>'
           '<button class="btn primary block" onclick="downloadDatabase()">' + _ic("dl") + 'Download mx-ui.json</button></div>',
           '<button class="btn" onclick="toggleModal(\'databaseModal\',false)">Close</button>', 760),
    _modal("qrModal", "QR codes", '<span id="qrTargetLabel">Config</span>',
           '<div class="qrs"><div class="qrc"><b style="font-size:13px">Config link</b><div class="qb"><img id="qrImage" alt="Config QR code"></div><p class="mono" id="qrTextPayload"></p>'
           '<button class="btn sm" onclick="copyText(document.getElementById(\'qrTextPayload\').textContent)">' + _ic("copy") + 'Copy config link</button></div>'
           '<div class="qrc"><b style="font-size:13px">Subscription link</b><div class="qb"><img id="qrSubImage" alt="Subscription QR code"></div><p class="mono" id="qrSubPayload"></p>'
           '<button class="btn sm" onclick="copyText(document.getElementById(\'qrSubPayload\').textContent)">' + _ic("copy") + 'Copy sub link</button></div></div>',
           '<button class="btn" onclick="toggleModal(\'qrModal\',false)">Close</button>', 640),
    _modal("settingsModal", "Settings", "Dashboard security.",
           '<div style="display:grid;gap:12px"><span class="sub">Change password</span>'
           + _fld("Current password", '<input type="password" id="settings-current-pw" class="input" autocomplete="current-password">')
           + _fld("New password", '<input type="password" id="settings-new-pw" class="input" placeholder="At least 4 characters" autocomplete="new-password">')
           + _fld("Confirm new password", '<input type="password" id="settings-confirm-pw" class="input" autocomplete="new-password">')
           + '<div id="settingsError" class="alert hidden" role="alert"></div><button class="btn primary" onclick="changePassword()">Update password</button></div>',
           '<button class="btn" onclick="toggleModal(\'settingsModal\',false)">Close</button>', 560),
    '<div id="confirmModal" class="modal top" role="alertdialog" aria-modal="true" aria-labelledby="confirmTitle"><div class="sheet" tabindex="-1" style="--w:380px"><div class="cen">'
    '<div class="bdg" id="confirmBadge">' + _ic("alert") + '</div><div><h3 id="confirmTitle">Confirm action</h3><p id="confirmMessage" style="margin-top:6px">Are you sure?</p></div>'
    '<div class="row2"><button class="btn" onclick="_confirmNo()">Cancel</button><button class="btn danger" id="confirmOk" onclick="_confirmYes()">Confirm</button></div></div></div></div>',
    '<div id="customAlert" class="modal top" role="alertdialog" aria-modal="true" aria-labelledby="alertTitle"><div class="sheet" tabindex="-1" style="--w:380px"><div class="cen">'
    '<div class="bdg info"><svg id="alertIcon" class="i"><use href="#info"/></svg></div><div><h3 id="alertTitle">Notification</h3><p id="alertMessage" style="margin-top:6px"></p></div>'
    '<button class="btn primary block" onclick="toggleModal(\'customAlert\',false)">OK</button></div></div></div>',
])

_DASH_BODY = """<body>
""" + _SPRITE + """
<header><div class="wrap">
  <div class="brand"><div class="logo">MX</div><div>MX-UI<small>v1.0.0</small></div><span class="pill ok hide-m"><i></i>Online</span></div>
  <div class="tools">""" + _TOOLS + """</div>
</div></header>

<main class="wrap">
  <section class="panel stats" aria-label="Totals">
    <div class="stat"><small>Traffic</small><b id="total-traffic" class="mono">0 MB</b></div>
    <div class="stat"><small>Usage</small><b id="total-usage" class="mono">0 GB</b></div>
    <div class="stat"><small>Inbounds</small><b id="total-inbounds" class="mono">0</b></div>
    <div class="stat"><small>Connections</small><b id="active-connections" class="mono">0</b></div>
  </section>

  <section aria-label="System diagnostics">
    <div class="sec-h"><h2>System</h2>
      <button class="link-btn" id="toggleSystemBtn" aria-expanded="false" onclick="toggleSystemDetails()">""" + _ic("chev") + """<span id="toggleSystemText">Show more</span></button></div>
    <div class="panel rings">""" + _RINGS_HTML + """</div>
    <div class="exp" id="systemDetailsWrapper"><div><div class="dg">""" + _DETAILS_HTML + """</div></div></div>
  </section>

  <section class="panel" style="padding:0;overflow:hidden" aria-label="Configs">
    <div class="sec-h" style="padding:18px 20px 0;margin:0 0 14px">
      <div><h2>Configs</h2><p class="mut" style="font-size:13px">All V2Ray configurations</p></div>
      <div class="sec-r"><input id="search" class="input search" type="search" placeholder="Search configs" aria-label="Search configs">
        <button class="btn primary" onclick="toggleModal('inboundModal',true)">""" + _ic("plus") + """<span>Add config</span></button></div>
    </div>
    <div id="config-list" style="border-top:1px solid var(--line)"></div>
    <div class="dfoot"><span>MX-UI v1.0.0 · Created by Muvixo</span><span>Core uptime <b id="uptime-display" class="mono">00:00:00</b> · API <b style="color:var(--acc)">Connected</b></span></div>
  </section>
</main>
""" + _MODALS + """
<div id="toast" class="toast" role="status"></div>
"""

_DASH_JS = """
var $=function(id){return document.getElementById(id);};
var set=function(i,v){var e=$(i);if(e)e.textContent=v;};
var esc=function(s){return String(s||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
var ic=function(n){return '<svg class="i"><use href="#'+n+'"/></svg>';};
var J=function(u,b,m){return fetch(u,{method:m||'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});};
var jerr=async function(r,d){try{var j=await r.json();return j.detail||d;}catch(e){return d;}};
var fmtBytes=function(b){b=b||0;if(b<1024)return b+' B';if(b<1048576)return (b/1024).toFixed(1)+' KB';if(b<1073741824)return (b/1048576).toFixed(2)+' MB';return (b/1073741824).toFixed(2)+' GB';};
var fmtMB=function(m){return m>=1024?(m/1024).toFixed(2)+' GB':m.toFixed(1)+' MB';};
var fmtGB=function(g){return g>=1024?(g/1024).toFixed(2)+' TB':g.toFixed(1)+' GB';};

function toggleTheme(){
  var d=document.documentElement;
  d.dataset.theme=d.dataset.theme==='dark'?'light':'dark';
  try{localStorage.setItem('mx-theme',d.dataset.theme);}catch(e){}
}

var stack=[];
var confirmRes=null;
var onOpen={
  databaseModal:function(){loadDatabaseInfo();},
  healthModal:function(){loadHealthConfigs();},
  settingsModal:function(){resetSettings();},
  ipSuggestModal:function(){initIPModal();}
};

function toggleModal(id,show){
  var m=$(id);
  if(!m)return;
  if(show){
    if(stack.indexOf(id)>=0)return;
    m._from=document.activeElement;
    stack.push(id);
    m.classList.add('open');
    document.body.classList.add('lock');
    setTimeout(function(){
      var sh=m.querySelector('.sheet');
      if(sh)sh.focus();
    },30);
    if(onOpen[id])onOpen[id]();
  }else{
    var i=stack.indexOf(id);
    if(i<0)return;
    stack.splice(i,1);
    m.classList.remove('open');
    if(!stack.length)document.body.classList.remove('lock');
    if(id==='confirmModal')answer(false);
    if(m._from&&m._from.focus)m._from.focus();
  }
}

document.querySelectorAll('.modal').forEach(function(m){
  m.addEventListener('pointerdown',function(e){if(e.target===m)toggleModal(m.id,false);});
});

document.addEventListener('keydown',function(e){
  var id=stack[stack.length-1];
  if(!id)return;
  if(e.key==='Escape'){toggleModal(id,false);return;}
});

function answer(v){if(confirmRes){var r=confirmRes;confirmRes=null;r(v);}}
function customConfirm(msg,ok,danger,title){
  set('confirmMessage',msg);
  set('confirmTitle',title||'Confirm action');
  var b=$('confirmOk');
  b.textContent=ok||'Confirm';
  b.className='btn '+(danger?'danger':'primary');
  $('confirmBadge').className='bdg'+(danger?'':' info');
  return new Promise(function(resolve){
    answer(false);
    confirmRes=resolve;
    toggleModal('confirmModal',true);
  });
}
function _confirmYes(){answer(true);toggleModal('confirmModal',false);}
function _confirmNo(){answer(false);toggleModal('confirmModal',false);}
function triggerAlert(title,msg,icon){
  set('alertTitle',title);
  set('alertMessage',msg);
  var ai=$('alertIcon');
  if(ai)ai.innerHTML='<use href="#'+(icon||'info')+'"/>';
  toggleModal('customAlert',true);
}

async function getCurrentPaths(){
  try{
    var r=await fetch('/api/current-paths');
    if(!r.ok)throw 0;
    return await r.json();
  }catch(e){
    return {dashboard:'/dashboard',login:'/login',sub:'/sub',setup:'/setup'};
  }
}
async function goLogin(){
  var p=await getCurrentPaths();
  try{await fetch('/api/logout',{method:'POST'});}catch(e){}
  location.href=p.login||'/login';
}

var sysOpen=false;
function toggleSystemDetails(){
  sysOpen=!sysOpen;
  var wrap=$('systemDetailsWrapper');
  if(wrap)wrap.classList.toggle('open',sysOpen);
  var btn=$('toggleSystemBtn');
  if(btn)btn.setAttribute('aria-expanded',String(sysOpen));
  set('toggleSystemText',sysOpen?'Show less':'Show more');
}

function ring(k,pct,val){
  pct=Math.min(100,Math.max(0,pct||0));
  var r=$('ring-'+k);
  if(r)r.setAttribute('stroke-dasharray',pct+' 100');
  set('ring-'+k+'-pct',pct.toFixed(1)+'%');
  set('ring-'+k+'-val',val);
}

async function updateStats(){
  try{
    var res=await fetch('/stats');
    var d=await res.json();
    var n=function(x){return Number(x)||0;};
    var tr=n(d.total_traffic_mb),cpu=n(d.cpu_percent),rT=n(d.ram_total_mb),rU=n(d.ram_used_mb),sT=n(d.swap_total_mb),sU=n(d.swap_used_mb),dT=n(d.disk_total_gb),dU=n(d.disk_used_gb);
    set('uptime-display',d.uptime||'00:00:00');
    set('total-traffic',fmtMB(tr));
    set('total-usage',(tr/1024).toFixed(2)+' GB');
    set('total-inbounds',d.links_count||0);
    set('active-connections',d.active_connections||0);
    ring('cpu',cpu,n(d.cpu_cores)+' cores');
    ring('ram',n(d.ram_percent),(rU/1024).toFixed(2)+' / '+(rT/1024).toFixed(2)+' GB');
    ring('swap',n(d.swap_percent),(sU/1024).toFixed(2)+' / '+(sT/1024).toFixed(2)+' GB');
    ring('disk',n(d.disk_percent),fmtGB(dU)+' / '+fmtGB(dT));

    var g=function(m){return (m/1024).toFixed(2)+' GB';};
    var S={
      'cpu-load-avg':cpu.toFixed(1)+'%',
      'cpu-cores-detail':d.cpu_cores?d.cpu_cores+' cores':'--',
      'cpu-user':(cpu*0.7).toFixed(1)+'%',
      'cpu-system':(cpu*0.3).toFixed(1)+'%',
      'cpu-idle':(100-cpu).toFixed(1)+'%',
      'ram-total-detail':g(rT),
      'ram-used-detail':g(rU),
      'ram-free-detail':g(Math.max(0,rT-rU)),
      'ram-available-detail':g(Math.max(0,rT-rU)),
      'ram-cached-detail':g(Math.max(0,rT-rU)*0.3),
      'swap-total-detail':g(sT),
      'swap-used-detail':g(sU),
      'swap-free-detail':g(Math.max(0,sT-sU)),
      'swap-usage-detail':n(d.swap_percent).toFixed(1)+'%',
      'disk-total-detail':fmtGB(dT),
      'disk-used-detail':fmtGB(dU),
      'disk-free-detail':fmtGB(Math.max(0,dT-dU)),
      'disk-usage-detail':n(d.disk_percent).toFixed(1)+'%',
      'network-total':fmtMB(tr),
      'network-requests':d.total_requests||0,
      'network-connections':d.active_connections||0,
      'network-errors':d.total_errors||0,
      'sys-uptime':d.uptime||'00:00:00',
      'sys-active-configs':d.active_links||0,
      'sys-total-configs':d.links_count||0,
      'sys-expired-configs':d.expired_links||0
    };
    for(var k in S){set(k,S[k]);}
  }catch(e){}
}

var links=[];
async function getLinks(){
  var r=await fetch('/api/links');
  if(r.status===401||r.status===403){location.href='/login';throw new Error('auth');}
  if(!r.ok)throw new Error('Failed to load configs');
  var d=await r.json();
  links=d.links||[];
  return links;
}

function row(l){
  var act=Boolean(l.active&&!l.expired);
  var def=Boolean(l.is_default);
  var proto=l.protocol||'vless-ws';
  var lim=Boolean(!l.limit_bytes);
  var used=l.used_bytes||0;
  var pct=lim?0:Math.min(100,(used/l.limit_bytes)*100);
  var sp=l.speed_limit_bytes>0?((l.speed_limit_bytes*8)/1048576).toFixed(1)+' Mbps':'Unlimited';
  var exp=l.expires_at?new Date(l.expires_at).toISOString().slice(0,10):'Unlimited';
  var ap=l.applied_ips_count||0;

  var out='<div class="row'+(def?' def':'')+'" data-uuid="'+esc(l.uuid)+'">';
  out+='<div><div class="name"><span class="tag acc">VLESS</span><b>'+esc(l.label||'Unnamed')+'</b>';
  out+='<span class="pill '+(act?'ok':'off')+'"><i></i>'+(act?'Active':'Inactive')+'</span>';
  if(def)out+='<span class="tag warn">Default</span>';
  if(ap)out+='<span class="tag">'+ap+' applied IP'+(ap>1?'s':'')+'</span>';
  out+='</div>';
  out+='<div class="meta"><span>Network <b>ws</b></span><span>Security <b>tls</b></span><span>Expiry <b>'+exp+'</b></span><span>Usage <b>'+fmtBytes(used)+' / '+(lim?'Unlimited':fmtBytes(l.limit_bytes))+'</b></span><span>IP <b>'+(l.ip_limit||'Unlimited')+'</b></span><span>Speed <b>'+sp+'</b></span>';
  if(l.note)out+='<span>Note <b>'+esc(l.note)+'</b></span>';
  out+='</div>';
  out+='<div class="bar '+(pct>90?'full':pct>70?'warn':'')+'"><i style="width:'+pct+'%"></i></div></div>';
  out+='<div class="ctl">';
  out+='<label class="sw"><input type="checkbox" data-t '+(act?'checked':'')+' '+(def?'disabled':'')+'><i></i><em>'+(act?'Enabled':'Disabled')+'</em></label>';
  out+='<div class="lk"><input class="input" readonly value="'+esc(l.vless_link)+'" aria-label="Config link"><button class="ib sm" data-a="copy" title="Copy link">'+ic('copy')+'</button></div>';
  out+='<button class="ib sm" data-a="qr" title="QR codes">'+ic('qr')+'</button>';
  out+='<button class="ib sm" data-a="portal" title="Subscription page">'+ic('open')+'</button>';
  if(def){
    out+='<span class="tag warn">Protected</span>';
  } else {
    out+='<button class="ib sm" data-a="edit" title="Edit">'+ic('edit')+'</button><button class="ib sm" data-a="reset" title="Reset traffic">'+ic('reset')+'</button><button class="ib sm danger" data-a="del" title="Delete">'+ic('trash')+'</button>';
  }
  out+='</div></div>';
  return out;
}

function renderLinks(){
  var q=$('search').value.trim().toLowerCase();
  var items=links.filter(function(l){return !q||String(l.label||'').toLowerCase().indexOf(q)>=0;});
  var c=$('config-list');
  if(!c)return;
  if(items.length){
    c.innerHTML=items.map(row).join('');
  } else {
    c.innerHTML='<div class="empty"><b>'+(links.length?'No matches':'No configs yet')+'</b>'+(links.length?'Try a different name.':'Select "Add config" to create your first one.')+'</div>';
  }
}

async function loadConfigs(){
  try{
    await getLinks();
    renderLinks();
    updateStats();
  }catch(e){}
}

var sInp=$('search');
if(sInp)sInp.oninput=renderLinks;

var cl=$('config-list');
if(cl){
  cl.addEventListener('click',function(e){
    var b=e.target.closest('[data-a]');
    if(!b)return;
    var r=b.closest('.row');
    if(!r)return;
    var l=links.find(function(x){return x.uuid===r.dataset.uuid;});
    if(!l)return;
    var act=b.dataset.a;
    if(act==='copy')copyText(l.vless_link);
    else if(act==='qr')openQrModal(l);
    else if(act==='portal')window.open('/sub/user?uuid='+encodeURIComponent(l.uuid),'_blank');
    else if(act==='edit')openEdit(l);
    else if(act==='reset')resetTraffic(l.uuid);
    else if(act==='del')deleteConfig(l.uuid);
  });
  cl.addEventListener('change',function(e){
    if(e.target.matches('[data-t]')){
      var r=e.target.closest('.row');
      if(r)toggleConfigStatus(r.dataset.uuid,e.target.checked,e.target);
    }
  });
}

async function toggleConfigStatus(uuid,on,cb){
  try{
    var r=await J('/api/links/'+uuid+'/toggle',{active:on},'PATCH');
    if(!r.ok)throw 0;
    toast('Config '+(on?'enabled':'disabled'),'ok');
    loadConfigs();
  }catch(e){
    toast('Could not change status','err');
    cb.checked=!on;
  }
}

var cfgBody=function(p){
  var g=function(k){var el=$(p+'-'+k);return el?el.value:'';};
  return {
    label:g('label').trim()||'New Config',
    protocol:g('protocol')||'vless-ws',
    fingerprint:g('fp')||'chrome',
    alpn:g('alpn').trim(),
    limit_value:parseFloat(g('limit'))||0,
    limit_unit:'MB',
    expires_days:parseInt(g('expiry'),10)||0,
    ip_limit:parseInt(g('iplimit'),10)||0,
    speed_limit_value:parseFloat(g('speed'))||0,
    speed_limit_unit:g('speed-unit')||'MBIT',
    note:g('note').trim()
  };
};

async function createConfig(){
  try{
    var r=await J('/api/links',cfgBody('new'));
    if(!r.ok)throw new Error(await jerr(r,'Could not create config'));
    toggleModal('inboundModal',false);
    toast('Config created','ok');
    ['label','alpn','note'].forEach(function(k){var el=$('new-'+k);if(el)el.value='';});
    ['limit','expiry','iplimit','speed'].forEach(function(k){var el=$('new-'+k);if(el)el.value='0';});
    loadConfigs();
  }catch(e){
    toast(e.message,'err');
  }
}

function openEdit(l){
  var v=function(k,val){var el=$('edit-'+k);if(el)el.value=val;};
  $('edit-uuid').value=l.uuid;
  set('editNodeTitle',l.label);
  v('label',l.label||'');
  v('protocol',l.protocol||'vless-ws');
  v('fp',l.fingerprint||'chrome');
  v('alpn',l.alpn||'');
  toggleModal('editModal',true);
}

async function saveEdit(){
  try{
    var r=await J('/api/links/'+$('edit-uuid').value,cfgBody('edit'),'PATCH');
    if(!r.ok)throw new Error(await jerr(r,'Could not update config'));
    toggleModal('editModal',false);
    toast('Config updated','ok');
    loadConfigs();
  }catch(e){
    toast(e.message,'err');
  }
}

async function deleteConfig(uuid){
  var ok=await customConfirm('Delete this configuration? This cannot be undone.','Delete',true,'Delete config');
  if(!ok)return;
  try{
    var r=await fetch('/api/links/'+uuid,{method:'DELETE'});
    if(!r.ok)throw 0;
    toast('Config deleted','ok');
    loadConfigs();
  }catch(e){
    toast('Could not delete config','err');
  }
}

async function resetTraffic(uuid){
  var ok=await customConfirm('Reset traffic counters for this config?','Reset',true,'Reset traffic');
  if(!ok)return;
  try{
    var r=await fetch('/api/links/'+uuid+'/reset-traffic',{method:'POST'});
    if(!r.ok)throw 0;
    toast('Traffic reset','ok');
    loadConfigs();
  }catch(e){
    toast('Could not reset traffic','err');
  }
}

async function qrInto(id,data){
  var img=$(id);
  if(!img)return;
  img.removeAttribute('src');
  var u='/api/qr?data='+encodeURIComponent(data)+'&size=300';
  try{
    var res=await fetch(u);
    var d=await res.json();
    if(d.qr)img.src=d.qr;
  }catch(e){
    img.src=u+'&format=image';
  }
}

function openQrModal(l){
  set('qrTargetLabel',l.label||'Config');
  set('qrTextPayload',l.vless_link||'');
  set('qrSubPayload',l.sub_url||'');
  qrInto('qrImage',l.vless_link||'');
  qrInto('qrSubImage',l.sub_url||'');
  toggleModal('qrModal',true);
}

var domainSt={is_railway:false,host:''};
var ips=[];
async function initIPModal(){
  await checkDomain();
  if(!domainSt.is_railway)fetchSuggestions();
}
async function checkDomain(){
  try{
    var r=await fetch('/api/domain/check');
    domainSt=await r.json();
    renderDomain();
  }catch(e){
    toast('Could not check domain','err');
  }
}
function renderDomain(){
  var r=Boolean(domainSt.is_railway);
  var n=$('domainStatus');
  if(n){
    n.className='note '+(r?'warn':'ok');
    n.innerHTML=ic(r?'alert':'ok')+'<div><b>'+(r?'Railway default domain detected':'Custom domain')+'</b><p>'+(r?'IP suggestions require a custom domain.':'IP suggestions are ready.')+'</p><p class="mono">'+esc(domainSt.host)+'</p></div>';
  }
  var ib=$('ipBody');
  if(ib)ib.classList.toggle('hidden',r);
  var lb=$('loadIpsBtn');
  if(lb)lb.disabled=r;
}
async function fetchSuggestions(){
  try{
    var r=await fetch('/api/ips/suggest');
    var d=await r.json();
    ips=d.ips||[];
    var sl=$('suggestList');
    if(sl){
      if(ips.length){
        sl.innerHTML=ips.map(function(ip){
          return '<label class="chk mono"><input type="checkbox" class="suggest-ip-checkbox" value="'+esc(ip)+'" checked>'+esc(ip)+'</label>';
        }).join('');
      } else {
        sl.innerHTML='<p class="mut" style="grid-column:1/-1;text-align:center;font-size:13px">No IPs available.</p>';
      }
    }
    await loadApplyTargets();
    set('applyStatus',ips.length?ips.length+' IP(s) loaded':'No IPs loaded');
  }catch(e){
    toast('Could not load IP suggestions','err');
  }
}
async function loadApplyTargets(){
  try{await getLinks();}catch(e){return;}
  var atl=$('applyTargetList');
  if(atl){
    if(links.length){
      atl.innerHTML=links.map(function(l){
        return '<label class="chk"><input type="checkbox" class="suggest-target-checkbox" value="'+esc(l.uuid)+'"><span>'+esc(l.label)+'</span>'+(l.applied_ips_count?'<span class="tag acc">'+l.applied_ips_count+' IP'+(l.applied_ips_count>1?'s':'')+'</span>':'')+'</label>';
      }).join('');
    } else {
      atl.innerHTML='<p class="mut" style="font-size:12px;padding:8px">Create a config first.</p>';
    }
  }
  updateApplyBtn();
}
function updateApplyBtn(){
  var tg=document.querySelectorAll('.suggest-target-checkbox:checked').length;
  var b=$('applySuggestBtn');
  if(b)b.disabled=!tg||!ips.length;
}
var atlEl=$('applyTargetList');
if(atlEl)atlEl.addEventListener('change',updateApplyBtn);

async function applySuggestedIPs(){
  var sel=[];
  document.querySelectorAll('.suggest-ip-checkbox:checked').forEach(function(x){sel.push(x.value);});
  var tg=[];
  document.querySelectorAll('.suggest-target-checkbox:checked').forEach(function(x){tg.push(x.value);});
  if(!sel.length)return toast('Select at least one IP','err');
  if(!tg.length)return toast('Select at least one config','err');
  var ok=await customConfirm('Apply '+sel.length+' IP(s) to '+tg.length+' config(s)?','Apply',false,'Apply IPs');
  if(!ok)return;
  var b=$('applySuggestBtn');
  b.disabled=true;
  b.textContent='Applying...';
  try{
    var r=await J('/api/ips/apply',{ips:sel,target_uuids:tg});
    if(!r.ok)throw new Error(await jerr(r,'Apply failed'));
    toast('IPs applied successfully','ok');
    loadConfigs();
    set('applyStatus','Applied to '+tg.length+' config(s)');
  }catch(e){
    toast(e.message,'err');
  }finally{
    b.innerHTML=ic('check')+'Apply to selected';
    updateApplyBtn();
  }
}

async function loadHealthConfigs(){
  set('healthStatus','Select configs to test');
  $('healthResults').innerHTML='';
  try{await getLinks();}catch(e){toast('Could not load configs','err');return;}
  var hl=$('healthConfigList');
  if(hl){
    if(links.length){
      hl.innerHTML=links.map(function(l){
        return '<label class="chk"><input type="checkbox" class="health-config-checkbox" value="'+esc(l.uuid)+'"><span>'+esc(l.label)+'</span><span class="tag '+(l.active?'acc':'')+'">'+(l.active?'Active':'Inactive')+'</span></label>';
      }).join('');
    } else {
      hl.innerHTML='<p class="mut" style="font-size:13px;padding:8px;text-align:center">No configurations found.</p>';
    }
  }
  updateHealthBtn();
}
function updateHealthBtn(){
  var c=document.querySelectorAll('.health-config-checkbox:checked').length;
  var b=$('healthTestBtn');
  if(b)b.disabled=!c;
  set('healthStatus',c?c+' config(s) selected':'Select at least one config');
}
var hclEl=$('healthConfigList');
if(hclEl)hclEl.addEventListener('change',updateHealthBtn);

async function testSelectedConfigs(){
  var uuids=[];
  document.querySelectorAll('.health-config-checkbox:checked').forEach(function(x){uuids.push(x.value);});
  if(!uuids.length)return;
  var b=$('healthTestBtn');
  b.disabled=true;
  b.textContent='Testing...';
  set('healthStatus','Testing...');
  try{
    var r=await J('/api/configs/test',{uuids:uuids});
    if(!r.ok)throw new Error(await jerr(r,'Test failed'));
    var d=await r.json();
    var res=d.results||{};
    var ks=Object.keys(res);
    var hr=$('healthResults');
    if(hr){
      if(ks.length){
        var rows=ks.map(function(k){
          var x=res[k];
          var c=links.find(function(l){return l.uuid===k;});
          return '<tr><td>'+esc(c?c.label:k.slice(0,8))+'</td><td class="'+(x.healthy?'good':'bad')+'">'+(x.healthy?'Healthy':'Unhealthy')+'</td><td class="mono">'+(x.latency?x.latency.toFixed(1)+' ms':'-')+'</td><td>'+esc(x.error||'-')+'</td></tr>';
        }).join('');
        hr.innerHTML='<div class="tw c2" style="padding:6px"><table class="tbl"><thead><tr><th>Config</th><th>Status</th><th>Latency</th><th>Error</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
      } else {
        hr.innerHTML='<p class="mut">No results.</p>';
      }
    }
    set('healthStatus','Test completed');
  }catch(e){
    toast(e.message,'err');
    set('healthStatus','Test failed');
  }finally{
    b.innerHTML=ic('play')+'Test selected';
    updateHealthBtn();
  }
}

async function loadDatabaseInfo(){
  try{
    await getLinks();
    var tr=links.reduce(function(a,l){return a+(l.used_bytes||0);},0);
    set('db-total-configs',links.length);
    set('db-active-configs',links.filter(function(l){return l.active;}).length);
    set('db-total-traffic',fmtBytes(tr));
    set('db-last-saved',new Date().toLocaleString());
    var dbBody=$('dbConfigsBody');
    if(dbBody){
      if(links.length){
        dbBody.innerHTML=links.map(function(l){
          return '<tr><td>'+esc(l.label||'Unnamed')+'</td><td class="mono">'+esc(String(l.uuid).slice(0,12))+'...</td><td class="r mono">'+fmtBytes(l.used_bytes)+'</td><td class="r mono">'+(l.limit_bytes?fmtBytes(l.limit_bytes):'Unlimited')+'</td><td><span class="pill '+(l.active?'ok':'off')+'"><i></i>'+(l.active?'Active':'Inactive')+'</span></td><td class="r mono">'+(l.connected_ips||0)+'</td></tr>';
        }).join('');
      } else {
        dbBody.innerHTML='<tr><td colspan="6" style="text-align:center;color:var(--mut)">No configurations found</td></tr>';
      }
    }
  }catch(e){
    toast('Could not load database info','err');
  }
}

async function downloadDatabase(){
  try{
    var r=await fetch('/api/database/export');
    if(!r.ok)throw new Error('Export failed');
    var d=await r.json();
    var blob=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});
    var a=document.createElement('a');
    var u=URL.createObjectURL(blob);
    a.href=u;
    a.download='mx-ui.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(u);
    toast('Database downloaded','ok');
  }catch(e){
    toast(e.message,'err');
  }
}

function resetSettings(){
  ['current','new','confirm'].forEach(function(k){
    var el=$('settings-'+k+'-pw');
    if(el)el.value='';
  });
  var err=$('settingsError');
  if(err)err.classList.add('hidden');
}

async function changePassword(){
  var cur=$('settings-current-pw').value,nw=$('settings-new-pw').value,cf=$('settings-confirm-pw').value,er=$('settingsError');
  er.classList.add('hidden');
  var fail=function(m){er.textContent=m;er.classList.remove('hidden');};
  if(!cur||!nw||!cf)return fail('All fields are required.');
  if(nw.length<4)return fail('New password must be at least 4 characters.');
  if(nw!==cf)return fail("New password and confirmation do not match.");
  try{
    var r=await J('/api/change-password',{current_password:cur,new_password:nw});
    if(!r.ok)throw new Error(await jerr(r,'Could not update password'));
    toggleModal('settingsModal',false);
    triggerAlert('Password updated','Your password was changed. You will be signed out.','ok');
    setTimeout(goLogin,2000);
  }catch(e){
    fail(e.message);
  }
}

loadConfigs();
setInterval(updateStats,5000);
setInterval(loadConfigs,15000);
"""

DASHBOARD_HTML = _page("MX-UI v1.0.0", _DASH_CSS, _DASH_BODY + "<script>" + _UTIL_JS + _DASH_JS + "</script>\n</body>\n</html>")


# ==================== LOGS PAGE (dashboard) ====================
_LOGS_CSS = """
.logs-wrap{max-width:1100px;margin:0 auto;padding:0 20px}
.logs-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin:24px 0 12px}
.logs-head h1{font-size:22px;font-weight:800}
.logs-tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.logs-tools select,.logs-tools input{height:36px;padding:0 10px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:inherit;font:13px var(--mono)}
.logs-panel{background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.logs-ports{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;padding:16px;border-bottom:1px solid var(--line)}
.logs-port{display:flex;justify-content:space-between;gap:8px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;font-size:13px}
.logs-port b{font:600 13px var(--mono)}
.logs-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px}
.logs-dot.ok{background:var(--acc)}
.logs-dot.bad{background:var(--bad)}
.logs-stream{max-height:calc(100vh - 280px);overflow:auto;background:#0c1112;color:#e2e8f0;font:12px/1.55 var(--mono)}
.logs-row{display:grid;grid-template-columns:150px 70px 1fr;gap:12px;padding:6px 14px;border-bottom:1px solid rgba(255,255,255,.05)}
.logs-row:hover{background:rgba(255,255,255,.04)}
.logs-row .t{color:#7f8b91}
.logs-row .lv{font-weight:700;text-transform:uppercase;font-size:11px}
.logs-row.info .lv{color:#37cbb2}
.logs-row.warning .lv{color:#e0b25a}
.logs-row.error .lv{color:#ff7b67}
.logs-row .m{white-space:pre-wrap;word-break:break-word}
.logs-empty{padding:36px;text-align:center;color:#7f8b91}
.logs-foot{display:flex;justify-content:space-between;padding:10px 16px;border-top:1px solid var(--line);font-size:12px;color:var(--mut)}
@media(max-width:640px){.logs-row{grid-template-columns:1fr}.logs-row .t,.logs-row .lv{display:none}}
"""

LOGS_HTML = _page("Logs - MX-UI", _LOGS_CSS, """<body>
<header><div class="wrap logs-wrap" style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--line)">
  <div class="brand"><div class="logo">MX</div><div>MX-UI<small>Logs</small></div></div>
  <div class="tools"><button class="btn sm" onclick="location.href='/dashboard'">&larr; Dashboard</button></div>
</div></header>
<main class="logs-wrap">
  <div class="logs-head">
    <h1>Xray logs</h1>
    <div class="logs-tools">
      <select id="lvl" onchange="loadLogs()">
        <option value="">All levels</option>
        <option value="info">Info</option>
        <option value="warning">Warning</option>
        <option value="error">Error</option>
      </select>
      <label style="display:flex;align-items:center;gap:6px;font-size:13px">
        <input type="checkbox" id="auto" checked> Auto-refresh
      </label>
      <button class="btn sm" onclick="loadLogs()">Refresh</button>
      <button class="btn sm danger" onclick="clearLogs()">Clear</button>
    </div>
  </div>
  <div class="logs-panel">
    <div class="logs-ports" id="portsBox"></div>
    <div class="logs-stream" id="stream"><div class="logs-empty">Loading...</div></div>
    <div class="logs-foot">
      <span id="count">0 entries</span>
      <span id="updated">-</span>
    </div>
  </div>
</main>
<div id="toast" class="toast"></div>
<script>""" + _UTIL_JS + """
var $=function(id){return document.getElementById(id);};
var esc=function(s){return String(s||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};

async function loadPorts(){
  try{
    var r=await fetch('/api/logs/ports');
    var d=await r.json();
    var listen=d.listening||{};
    var keys=Object.keys(listen);
    $('portsBox').innerHTML=keys.map(function(k){
      var ok=!!listen[k];
      return '<div class="logs-port"><span><span class="logs-dot '+(ok?'ok':'bad')+'"></span>'+esc(k)+'</span><b>'+(ok?'LISTENING':'DOWN')+'</b></div>';
    }).join('') +
    '<div class="logs-port"><span>version</span><b>'+esc(d.xray_version||'-')+'</b></div>' +
    '<div class="logs-port"><span>pid</span><b>'+esc(d.xray_pid==null?'-':d.xray_pid)+'</b></div>' +
    '<div class="logs-port"><span>running</span><b>'+(d.xray_running?'YES':'NO')+'</b></div>';
  }catch(e){}
}

async function loadLogs(){
  var lvl=$('lvl').value;
  var url='/api/logs?limit=500'+(lvl?'&level='+encodeURIComponent(lvl):'');
  try{
    var r=await fetch(url);
    var d=await r.json();
    var logs=d.logs||[];
    var box=$('stream');
    if(!logs.length){box.innerHTML='<div class="logs-empty">No logs yet.</div>';}
    else{
      box.innerHTML=logs.map(function(x){
        var lv=esc(x.level||'info');
        return '<div class="logs-row '+lv+'"><span class="t">'+esc(x.time)+'</span><span class="lv">'+lv+'</span><span class="m">'+esc(x.msg)+'</span></div>';
      }).join('');
    }
    $('count').textContent=logs.length+' entries';
    $('updated').textContent='updated '+new Date().toLocaleTimeString();
  }catch(e){}
}

async function clearLogs(){
  if(!confirm('Clear the in-memory logs?'))return;
  try{
    await fetch('/api/logs/clear',{method:'POST'});
    toast('Logs cleared','ok');
    loadLogs();
  }catch(e){toast('Failed','err');}
}

function tick(){ if($('auto').checked){ loadLogs(); loadPorts(); } }
loadLogs();loadPorts();
setInterval(tick,3000);
</script>
</body>
</html>""")

# ==================== LOGS PAGE (dashboard) ====================
_LOGS_CSS = """
.logs-shell{max-width:1180px;margin:0 auto;padding:0 16px 40px}
.logs-bar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:12px 0;margin-bottom:18px}
.logs-bar-inner{max-width:1180px;margin:0 auto;padding:0 16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.logs-title{font-size:19px;font-weight:800;letter-spacing:-.02em;margin-right:auto}
.logs-controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.logs-controls select{height:36px;padding:0 10px;border:1px solid var(--line);border-radius:9px;background:var(--surface);color:inherit;font:13px var(--ui);cursor:pointer}
.logs-controls select:focus{outline:none;border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.logs-auto{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--mut);cursor:pointer;user-select:none;padding:0 4px}
.logs-auto input{accent-color:var(--acc);width:15px;height:15px;cursor:pointer}
.logs-btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;height:36px;padding:0 14px;border:1px solid var(--line);border-radius:9px;background:var(--surface);color:inherit;font:600 13px var(--ui);cursor:pointer;transition:background .15s,border-color .15s}
.logs-btn:hover{background:var(--sunk)}
.logs-btn.danger:hover{background:var(--bad-soft);color:var(--bad);border-color:transparent}
.logs-btn svg{width:15px;height:15px}

.logs-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:14px}
.logs-card{display:flex;align-items:center;gap:10px;padding:12px 14px;background:var(--surface);border:1px solid var(--line);border-radius:12px;min-width:0}
.logs-card .dot{width:9px;height:9px;border-radius:50%;flex:none}
.logs-card .dot.ok{background:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.logs-card .dot.bad{background:var(--bad);box-shadow:0 0 0 3px var(--bad-soft)}
.logs-card .txt{min-width:0;flex:1}
.logs-card .lbl{font-size:11px;color:var(--mut);font-weight:600;text-transform:uppercase;letter-spacing:.03em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logs-card .val{font:600 13px var(--mono);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px}

.logs-panel{background:#0c1112;border:1px solid var(--line);border-radius:14px;overflow:hidden}
.logs-stream{max-height:calc(100vh - 300px);overflow-y:auto;overflow-x:hidden;font:12.5px/1.6 var(--mono);color:#cbd5dc;overscroll-behavior:contain}
.logs-row{display:grid;grid-template-columns:132px 66px 1fr;gap:10px;padding:7px 14px;border-bottom:1px solid rgba(255,255,255,.045);align-items:start}
.logs-row:last-child{border-bottom:0}
.logs-row:hover{background:rgba(255,255,255,.035)}
.logs-row .t{color:#6b7981;font-size:11.5px;white-space:nowrap;padding-top:2px}
.logs-row .lv{font-weight:700;font-size:10px;letter-spacing:.05em;text-transform:uppercase;padding-top:3px}
.logs-row.info .lv{color:#37cbb2}
.logs-row.warning .lv{color:#e0b25a}
.logs-row.error .lv{color:#ff7b67}
.logs-row .m{white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere;min-width:0}
.logs-empty{padding:56px 20px;text-align:center;color:#6b7981;font:13px var(--ui)}
.logs-empty svg{width:34px;height:34px;opacity:.35;margin-bottom:10px;stroke-width:1.5}
.logs-foot{display:flex;justify-content:space-between;gap:10px;padding:10px 16px;border-top:1px solid rgba(255,255,255,.06);font:12px var(--mono);color:#6b7981;flex-wrap:wrap}

@media (max-width:720px){
  .logs-bar{padding:10px 0}
  .logs-bar-inner{padding:0 12px}
  .logs-title{font-size:16px;flex:1 1 100%;order:-1;margin-bottom:6px}
  .logs-controls{width:100%;gap:6px}
  .logs-controls select{flex:1;min-width:0}
  .logs-btn{padding:0 11px;height:34px;font-size:12.5px}
  .logs-shell{padding:0 12px 32px}
  .logs-cards{grid-template-columns:1fr 1fr;gap:8px}
  .logs-card{padding:10px 12px}
  .logs-card .val{font-size:12px}
  .logs-stream{max-height:calc(100vh - 260px);font-size:12px}
  .logs-row{grid-template-columns:1fr;gap:2px;padding:9px 12px}
  .logs-row .t{font-size:10.5px}
  .logs-row .lv{font-size:9.5px;padding-top:0}
  .logs-row .m{font-size:12px;margin-top:2px}
}
@media (max-width:380px){.logs-cards{grid-template-columns:1fr}}
"""

LOGS_HTML = _page("Logs - MX-UI", _LOGS_CSS, """<body>
<div class="logs-bar">
  <div class="logs-bar-inner">
    <div class="brand" style="flex:none"><div class="logo">MX</div></div>
    <div class="logs-title">Xray Logs</div>
    <div class="logs-controls">
      <select id="lvl" onchange="loadLogs()">
        <option value="">All levels</option>
        <option value="info">Info</option>
        <option value="warning">Warning</option>
        <option value="error">Error</option>
      </select>
      <label class="logs-auto"><input type="checkbox" id="auto" checked><span>Auto</span></label>
      <button class="logs-btn" onclick="loadLogs();loadPorts()" title="Refresh">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-15-6.7L3 8M3 3v5h5M3 12a9 9 0 0 0 15 6.7L21 16M21 21v-5h-5"/></svg>
      </button>
      <button class="logs-btn danger" onclick="clearLogs()" title="Clear">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
      </button>
      <button class="logs-btn" onclick="location.href='/dashboard'">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        <span>Back</span>
      </button>
    </div>
  </div>
</div>
<main class="logs-shell">
  <div class="logs-cards" id="portsBox"></div>
  <div class="logs-panel">
    <div class="logs-stream" id="stream">
      <div class="logs-empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m4 17 6-6-6-6M12 19h8"/></svg><div>Loading...</div></div>
    </div>
    <div class="logs-foot"><span id="count">0 entries</span><span id="updated">-</span></div>
  </div>
</main>
<div id="toast" class="toast"></div>
<script>__UTIL_JS__
var $=function(id){return document.getElementById(id);};
var esc=function(s){return String(s||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
async function loadPorts(){
  try{
    var r=await fetch('/api/logs/ports'); var d=await r.json();
    var listen=d.listening||{}; var cards=[];
    Object.keys(listen).forEach(function(k){
      var ok=!!listen[k];
      cards.push('<div class="logs-card"><span class="dot '+(ok?'ok':'bad')+'"></span><div class="txt"><div class="lbl">'+esc(k)+'</div><div class="val">'+(ok?'LISTENING':'DOWN')+'</div></div></div>');
    });
    cards.push('<div class="logs-card"><span class="dot '+(d.xray_running?'ok':'bad')+'"></span><div class="txt"><div class="lbl">Process</div><div class="val">'+(d.xray_running?'RUNNING pid '+esc(d.xray_pid==null?'-':d.xray_pid):'STOPPED')+'</div></div></div>');
    cards.push('<div class="logs-card"><span class="dot ok" style="background:var(--c2)"></span><div class="txt"><div class="lbl">Version</div><div class="val">'+esc(d.xray_version||'-')+'</div></div></div>');
    $('portsBox').innerHTML=cards.join('');
  }catch(e){}
}
function renderLogs(logs){
  var box=$('stream');
  if(!logs.length){
    box.innerHTML='<div class="logs-empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m4 17 6-6-6-6M12 19h8"/></svg><div>No logs yet.</div></div>';
    return;
  }
  var html='';
  for(var i=0;i<logs.length;i++){
    var x=logs[i]; var lv=esc(x.level||'info');
    html+='<div class="logs-row '+lv+'"><span class="t">'+esc(x.time)+'</span><span class="lv">'+lv+'</span><span class="m">'+esc(x.msg)+'</span></div>';
  }
  box.innerHTML=html;
}
async function loadLogs(){
  var lvl=$('lvl').value;
  var url='/api/logs?limit=500'+(lvl?'&level='+encodeURIComponent(lvl):'');
  try{
    var r=await fetch(url); var d=await r.json();
    renderLogs(d.logs||[]);
    $('count').textContent=(d.logs||[]).length+' entries';
    $('updated').textContent='updated '+new Date().toLocaleTimeString();
  }catch(e){}
}
async function clearLogs(){
  if(!confirm('Clear logs?'))return;
  try{await fetch('/api/logs/clear',{method:'POST'});toast('Logs cleared','ok');loadLogs();}catch(e){toast('Failed','err');}
}
function tick(){ if($('auto').checked){ loadLogs(); loadPorts(); } }
loadLogs();loadPorts();
setInterval(tick,3000);
</script>
</body>
</html>""")

# Substitute UTIL_JS placeholder now that _UTIL_JS is defined above.
LOGS_HTML = LOGS_HTML.replace('__UTIL_JS__', _UTIL_JS)
