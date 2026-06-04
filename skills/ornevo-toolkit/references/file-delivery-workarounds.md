# File Delivery Workarounds

When Hernan needs a file from the Mac mini but is remote (no direct machine access).

## Problem

WhatsApp (and some other messaging platforms) do not support direct file/MEDIA attachments through Hermes `send_message`. Public file sharing services (file.io, 0x0.st, transfer.sh) are frequently down or blocked.

## Solution: Temporary HTTP Server

Spin up a Python HTTP server on the Mac mini and share the Tailscale or public IP link.

### Steps

```bash
# 1. Navigate to the file's directory
cd /path/to/parent

# 2. Start HTTP server (background)
python3 -m http.server 9876 &

# 3. Get the Tailscale IP
tailscale status --self
# → e.g., 100.100.32.122

# 4. Share the link
# http://100.100.32.122:9876/filename.zip
```

### Fallback: Public IP

```bash
curl -s --max-time 5 https://api.ipify.org
# → e.g., 190.131.77.149
# http://190.131.77.149:9876/filename.zip
```

Note: Public IP requires inbound port access on the router. Tailscale IP works reliably when the remote device is on the same tailnet.

### Compression First

Always zip before sharing to reduce transfer size:

```bash
cd /path/to/parent
zip -r /tmp/export.zip folder/
# Typical compression: 70 MB → 14 MB for CSV files
```

### Cleanup

Remember to kill the HTTP server after download:

```bash
kill %1
# or
pkill -f "python3 -m http.server 9876"
```

## Platform Attachment Support

| Platform | File/MEDIA via `send_message` |
|----------|-------------------------------|
| Telegram | ✅ Yes |
| Discord | ✅ Yes |
| Matrix | ✅ Yes |
| Signal | ✅ Yes |
| Feishu | ✅ Yes |
| WeChat | ✅ Yes |
| Yuanbao | ✅ Yes |
| **WhatsApp** | ❌ No (text only) |

When the target platform is WhatsApp, use the HTTP server method above.
