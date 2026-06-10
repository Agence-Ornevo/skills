#!/usr/bin/env python3
"""Extract the 'hermes-agent' JWT API key from n8n production database.

Usage: python scripts/extract-n8n-jwt.py
Requires SSH access to production server (91.134.67.56).
"""

import subprocess
import sys

def extract_jwt():
    """Extract the hermes-agent JWT from n8n PostgreSQL database."""
    cmd = [
        "ssh", "ubuntu@91.134.67.56",
        "docker exec n8n-db psql -U n8n -d n8n -c "
        "\"COPY (SELECT \\\"apiKey\\\" FROM user_api_keys WHERE label='hermes-agent') TO '/tmp/hermes_key.txt';\" "
        "&& cat /tmp/hermes_key.txt"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"❌ Extraction failed: {result.stderr}", file=sys.stderr)
            return None
        
        jwt = result.stdout.strip()
        if not jwt or not jwt.startswith("eyJ"):
            print(f"❌ Invalid JWT format: {jwt[:50]}...", file=sys.stderr)
            return None
        
        print(f"✅ Extracted JWT ({len(jwt)} chars)")
        return jwt
        
    except subprocess.TimeoutExpired:
        print("❌ SSH command timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return None


def test_jwt(jwt: str) -> bool:
    """Verify the JWT works with n8n REST API."""
    import urllib.request
    import json
    
    url = "https://n8n.ornevo.pro/api/v1/workflows?active=true&limit=1"
    req = urllib.request.Request(url)
    req.add_header("X-N8N-API-KEY", jwt)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ JWT verified - {len(data.get('data', []))} active workflows found")
                return True
            else:
                print(f"❌ JWT test failed: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ JWT test error: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Extracting 'hermes-agent' JWT from n8n production...")
    jwt = extract_jwt()
    
    if jwt:
        print(f"\nJWT: {jwt}")
        print("\n🧪 Testing JWT against n8n API...")
        if test_jwt(jwt):
            print("\n✅ Success! Add to Hermes config:")
            print("  mcpServers:")
            print("    n8n:")
            print("      env:")
            print(f"        N8N_API_KEY: \"{jwt}\"")
            print("      headers:")
            print("        X-N8N-API-KEY: \"${N8N_API_KEY}\"")
        else:
            sys.exit(1)
    else:
        sys.exit(1)