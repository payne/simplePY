#!/usr/bin/env bash
set -euo pipefail

VENV="$(dirname "$0")/venv"
APP="$(dirname "$0")/app.py"
OUT="$(dirname "$0")/output.pdf"
PORT=5000
BASE="http://localhost:$PORT"

# ── start server ──────────────────────────────────────────────────────────────
"$VENV/bin/python" "$APP" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null; echo "Server stopped."' EXIT

echo "Server PID $SERVER_PID — waiting for it to be ready..."
for i in $(seq 1 20); do
  if curl -sf "$BASE/health" >/dev/null 2>&1; then
    echo "Server is up."
    break
  fi
  sleep 0.25
done

# ── build the request payload ─────────────────────────────────────────────────
PAYLOAD=$(cat <<'EOF'
{
  "template": "# {{ title }}\n\n**Prepared for:** {{ client }}\n\n---\n\n## Summary\n\n{{ summary }}\n\n## Line Items\n\n| Item | Qty | Unit Price | Total |\n|------|-----|-----------|-------|\n{% for item in items %}| {{ item.name }} | {{ item.qty }} | ${{ '%.2f' | format(item.price) }} | ${{ '%.2f' | format(item.qty * item.price) }} |\n{% endfor %}\n\n**Grand Total: ${{ '%.2f' | format(total) }}**\n\n---\n\n> Generated on {{ date }}\n",

  "data": {
    "title": "Invoice #1042",
    "client": "Acme Corp",
    "summary": "Professional services for Q2 2026 including consulting, development, and code review.",
    "items": [
      { "name": "Consulting",   "qty": 8,  "price": 200.00 },
      { "name": "Development",  "qty": 24, "price": 150.00 },
      { "name": "Code Review",  "qty": 4,  "price": 125.00 }
    ],
    "total": 5700.00,
    "date": "2026-06-09"
  }
}
EOF
)

# ── send request ──────────────────────────────────────────────────────────────
echo "Sending POST /render ..."
HTTP_CODE=$(curl -s -o "$OUT" -w "%{http_code}" \
  -X POST "$BASE/render" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if [ "$HTTP_CODE" = "200" ]; then
  echo "PDF written to $OUT ($(du -h "$OUT" | cut -f1))"
else
  echo "Request failed — HTTP $HTTP_CODE"
  cat "$OUT"
  exit 1
fi
