# Interactions Log

## 2026-06-09

### Request
Log all interactions to `interactions.md`. Create a Python program that in response to a POST containing a markdown template and JSON data produces a PDF. Create a shell script that demonstrates the program.

### Response
Created three files:

- **`app.py`** — Flask web server exposing `POST /render`. Accepts a JSON body with a `"template"` key (Markdown string with Jinja2 variables) and a `"data"` key (JSON object). Renders the template with the data, converts Markdown → HTML (via the `markdown` library with `tables`, `fenced_code`, and `nl2br` extensions), wraps it in styled HTML, and converts to PDF via WeasyPrint. Returns `application/pdf`.

- **`demo.sh`** — Shell script that starts the Flask server in the background, polls `/health` until ready, POSTs a sample invoice payload (title, client, line-item table, total, date), saves the returned PDF to `output.pdf`, and stops the server on exit.

- **`interactions.md`** (this file) — running log of session interactions.

Dependencies installed into `venv`: `flask`, `markdown`, `jinja2`, `weasyprint`.

Demo run produced `output.pdf` (16 KB) successfully.
