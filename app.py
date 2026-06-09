"""
Markdown-template + JSON data → PDF renderer.

POST /render
  Content-Type: application/json
  Body: { "template": "<markdown with Jinja2 vars>", "data": { ... } }

Returns the rendered PDF as application/pdf.
"""

import io
import time
from datetime import datetime, timezone
import markdown
from flask import Flask, request, send_file, jsonify
from jinja2 import Environment, BaseLoader, TemplateError
from weasyprint import HTML

app = Flask(__name__)
_start_time = time.monotonic()

HTML_WRAPPER = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; line-height: 1.6; color: #222; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
  h2 {{ border-bottom: 1px solid #aaa; padding-bottom: 4px; }}
  code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
  pre  {{ background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
  th {{ background: #f0f0f0; }}
  blockquote {{ border-left: 4px solid #ccc; margin: 0; padding-left: 16px; color: #555; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


@app.route("/")
def index():
    uptime_seconds = time.monotonic() - _start_time
    return jsonify(
        time_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        uptime_seconds=round(uptime_seconds, 2),
    )


@app.route("/render", methods=["POST"])
def render():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify(error="Request body must be JSON"), 400

    template_src = payload.get("template")
    data = payload.get("data", {})

    if not isinstance(template_src, str):
        return jsonify(error="'template' must be a string"), 400
    if not isinstance(data, dict):
        return jsonify(error="'data' must be a JSON object"), 400

    try:
        env = Environment(loader=BaseLoader())
        tmpl = env.from_string(template_src)
        rendered_md = tmpl.render(**data)
    except TemplateError as exc:
        return jsonify(error=f"Template error: {exc}"), 422

    body_html = markdown.markdown(
        rendered_md,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    full_html = HTML_WRAPPER.format(body=body_html)

    pdf_bytes = HTML(string=full_html).write_pdf()

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="output.pdf",
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(port=5000, debug=False)
