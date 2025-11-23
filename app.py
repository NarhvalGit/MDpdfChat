from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, send_file
from markdown import markdown
from xhtml2pdf import pisa

app = Flask(__name__)


def convert_markdown_to_html(content: str) -> str:
    """Convert Markdown text to sanitized HTML wrapped in a simple template."""
    html_body = markdown(content, extensions=["extra", "toc", "sane_lists"])
    return f"""
    <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                pre {{ background: #f5f5f5; padding: 12px; border-radius: 6px; overflow-x: auto; }}
                code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 4px; }}
                h1, h2, h3, h4, h5, h6 {{ margin-top: 1.4em; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
    </html>
    """


def html_to_pdf_bytes(html_content: str) -> bytes:
    """Render HTML to PDF and return the binary content."""
    pdf_buffer = BytesIO()
    result = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if result.err:
        raise ValueError("Kon het PDF-bestand niet genereren uit de opgegeven Markdown.")
    pdf_buffer.seek(0)
    return pdf_buffer.read()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    file = request.files.get("file")
    export_format = request.form.get("format")

    if not file or file.filename == "":
        return render_template("index.html", error="Upload een geldig Markdown-bestand."), 400

    if export_format not in {"html", "pdf"}:
        return render_template("index.html", error="Kies een exportformaat (HTML of PDF)."), 400

    content = file.stream.read().decode("utf-8", errors="ignore")
    html_content = convert_markdown_to_html(content)

    filename_stem = Path(file.filename).stem or "document"

    if export_format == "html":
        html_bytes = html_content.encode("utf-8")
        return send_file(
            BytesIO(html_bytes),
            mimetype="text/html",
            as_attachment=True,
            download_name=f"{filename_stem}.html",
        )

    pdf_bytes = html_to_pdf_bytes(html_content)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{filename_stem}.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
