
# MX-UI v1.0.0

Modern VLESS/XHTTP tunnel gateway with a beautiful dashboard, per‑config subscription links with volume, speed, IP limits, and expiry.

## Features

- VLESS over WebSocket and XHTTP (packet‑up, stream‑up)
- HTTP proxy
- Full management dashboard with live system stats (CPU, RAM, Swap, Storage)
- Unlimited configs with per‑link traffic, speed, IP limit, expiry, and active/inactive toggle
- **Local QR code generation** - No external API required, fully offline
- QR code for each link and subscription (clean QR without text)
- Fingerprint (uTLS) and ALPN per config
- Public subscription info page: `/sub/user?uuid=<uuid>` shows detailed usage, QR, and IPs
- Persistent state on disk (requires a persistent volume for `/data`)
- Customizable dashboard, login, and subscription paths

## Deploy

1. Fork this repo on GitHub.
2. Deploy on Railway (or any platform that supports Python).
3. Set `ADMIN_PASSWORD=MUVIXO` (or change it) and ensure a persistent volume is mounted at `/data`.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_PASSWORD` | Dashboard login password | `MUVIXO` |
| `SECRET_KEY` | Session signing secret (auto‑generated) | – |
| `DATA_DIR` | Persistent state directory | `/data` |
| `RAILWAY_PUBLIC_DOMAIN` | Public domain (set automatically on Railway) | `localhost` |
| `PORT` | Server port | `8000` |

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi==0.104.1`
- `uvicorn[standard]==0.24.0`
- `httpx==0.25.1`
- `websockets==12.0`
- `aiofiles>=23.2.1`
- `psutil==5.9.6`
- `qrcode>=7.4.2` - For local QR code generation
- `Pillow>=10.0.0` - For QR code image processing

## Usage

### Running the Server

```bash
python main.py
```

The server will start on port 8000 (or the port specified in `PORT` environment variable).

### Dashboard Access

- Dashboard: `https://your-domain/dashboard`
- Login with password `MUVIXO` (or your custom one)

### Configuration Management

- Create configs, copy their subscription links, view usage, and manage them via the UI.
- Each config supports:
  - Traffic limit (GB/MB/KB)
  - Expiry date
  - IP limit
  - Speed limit (Mbps/KB/s/MB/s)
  - Active/Inactive toggle
  - Protocol selection (VLESS+WS, XHTTP packet-up, XHTTP stream-up)
  - Fingerprint (uTLS) selection
  - ALPN configuration

### Subscription Links

End users can view their subscription info at:
- `https://your-domain/sub/user?uuid=<uuid>` - Full subscription page with QR code
- `https://your-domain/sub/<uuid>` - Raw subscription link (Base64 encoded)
- `https://your-domain/sub/<uuid>/info` - Simple subscription info

### QR Code Generation

QR codes are generated **locally** using the `qrcode` and `Pillow` libraries:
- No external API calls required
- Works completely offline
- Clean QR codes without text below the image
- Base64 encoded for direct HTML embedding
- Available via `/api/qr` endpoint

### Custom Paths

You can customize the dashboard, login, and subscription paths via the Settings panel:
- Dashboard path: `/dashboard` (default)
- Login path: `/login` (default)
- Subscription path: `/sub` (default)

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirect to dashboard |
| `/health` | GET | Health check |
| `/sub/user` | GET | Subscription page with QR |
| `/sub/{uuid}` | GET | Raw subscription link |
| `/sub/{uuid}/info` | GET | Subscription info |
| `/api/qr` | GET | Generate QR code (data parameter) |

### Protected Endpoints (Requires Auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard` | GET | Main dashboard |
| `/api/links` | GET | List all configs |
| `/api/links` | POST | Create new config |
| `/api/links/{uuid}` | PATCH | Update config |
| `/api/links/{uuid}` | DELETE | Delete config |
| `/api/links/{uuid}/toggle` | PATCH | Toggle config status |
| `/api/links/{uuid}/reset-traffic` | POST | Reset traffic usage |
| `/api/qr/{uuid}` | GET | Generate QR for config |
| `/stats` | GET | System statistics |
| `/api/connections` | GET | Active connections |
| `/api/activity` | GET | Activity logs |
| `/api/change-password` | POST | Change admin password |
| `/api/get-paths` | GET | Get current paths |
| `/api/update-path` | POST | Update path configuration |

## Project Structure

```
MX-UI/
├── Readme.md           # This file
├── main.py            # Main application
├── pages.py           # HTML templates
├── qr_generator.py    # Local QR code generator
├── relay_vless.py     # VLESS WebSocket relay
├── xhttp.py           # XHTTP protocol handler
├── speed_limit.py     # Speed limiting logic
├── requirements.txt   # Python dependencies
└── ee.py              # File tree generator
```

## Security

- Session-based authentication with secure cookies
- Password hashed with SHA256 + secret salt
- Automatic session expiration
- Per-config IP limiting
- Per-config traffic quotas
- Optional speed limiting

## Troubleshooting

### QR Codes Not Displaying

Ensure the following packages are installed:
```bash
pip install qrcode Pillow
```

### Port Already in Use

Change the port using the `PORT` environment variable:
```bash
PORT=8080 python main.py
```

### Persistent Storage

Make sure `/data` directory exists and is writable:
```bash
mkdir -p /data
chmod 755 /data
```

## License

MIT License

---

**Created by Muvixo**
