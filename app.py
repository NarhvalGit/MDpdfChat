from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, send_file
from markdown import markdown
from xhtml2pdf import pisa

app = Flask(__name__)


def convert_markdown_to_html(content: str, for_pdf: bool = False) -> str:
    """Convert Markdown text to sanitized HTML wrapped in a Narhval-styled template.

    Args:
        content: Markdown content to convert
        for_pdf: If True, uses direct hex values instead of CSS variables (xhtml2pdf compatible)
    """
    html_body = markdown(content, extensions=["extra", "toc", "sane_lists"])

    # For PDF generation, xhtml2pdf doesn't support CSS variables, so use direct hex values
    if for_pdf:
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    line-height: 1.6;
    color: #333;
    padding: 20px;
    background: #ffffff;
}

h1 {
    color: #014f67;
    font-size: 32px;
    font-weight: 700;
    margin: 20px 0 15px 0;
    padding-bottom: 10px;
    border-bottom: 4px solid #014f67;
}

h2 {
    color: #008080;
    font-size: 24px;
    font-weight: 600;
    margin: 20px 0 10px 0;
    padding-bottom: 8px;
    border-bottom: 3px solid #008080;
}

h3 {
    color: #014f67;
    font-size: 20px;
    font-weight: 600;
    margin: 18px 0 10px 0;
}

h4 {
    color: #008080;
    font-size: 18px;
    font-weight: 600;
    margin: 15px 0 8px 0;
}

h5, h6 {
    color: #014f67;
    font-size: 16px;
    font-weight: 600;
    margin: 12px 0 8px 0;
}

p {
    margin: 10px 0;
}

strong {
    color: #014f67;
    font-weight: 600;
}

em {
    color: #008080;
}

a {
    color: #008080;
    text-decoration: underline;
}

ul, ol {
    margin: 10px 0 10px 30px;
    padding: 0;
}

li {
    margin: 5px 0;
}

code {
    background: #f0f5f7;
    color: #014f67;
    padding: 2px 6px;
    font-family: Courier, monospace;
    font-size: 14px;
}

pre {
    background: #f5f9fa;
    border-left: 4px solid #008080;
    padding: 15px;
    margin: 15px 0;
}

pre code {
    background: none;
    padding: 0;
    color: #333;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
}

thead {
    background: #014f67;
    color: #fffbf0;
}

th {
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 10px 16px;
    border-bottom: 1px solid #e0e0e0;
}

tbody tr:nth-child(even) {
    background: #f9fafb;
}

blockquote {
    border-left: 4px solid #feb098;
    padding: 10px 15px;
    margin: 15px 0;
    background: #fef8f5;
    color: #014f67;
    font-style: italic;
}

hr {
    border: none;
    height: 3px;
    background: #008080;
    margin: 20px 0;
}

img {
    max-width: 100%;
    height: auto;
    margin: 15px 0;
}"""
    else:
        # For HTML export, use CSS variables (modern browser support)
        css_content = """
                :root {{
                    --narhval-primary: #014f67;
                    --narhval-teal: #008080;
                    --narhval-accent: #feb098;
                    --narhval-cream: #fffbf0;
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.7;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 40px 20px;
                    background: #ffffff;
                }}

                /* Headers */
                h1 {{
                    color: var(--narhval-primary);
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin: 2rem 0 1.5rem 0;
                    padding-bottom: 0.75rem;
                    border-bottom: 4px solid var(--narhval-primary);
                    line-height: 1.3;
                }}

                h1:first-child {{
                    margin-top: 0;
                }}

                h2 {{
                    color: var(--narhval-teal);
                    font-size: 2rem;
                    font-weight: 600;
                    margin: 2rem 0 1rem 0;
                    padding-bottom: 0.5rem;
                    border-bottom: 3px solid var(--narhval-teal);
                    line-height: 1.3;
                }}

                h3 {{
                    color: var(--narhval-primary);
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin: 1.75rem 0 1rem 0;
                    line-height: 1.3;
                }}

                h4 {{
                    color: var(--narhval-teal);
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin: 1.5rem 0 0.875rem 0;
                    line-height: 1.3;
                }}

                h5, h6 {{
                    color: var(--narhval-primary);
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin: 1.25rem 0 0.75rem 0;
                    line-height: 1.3;
                }}

                /* Paragraphs and text */
                p {{
                    margin: 1rem 0;
                    text-align: justify;
                }}

                strong {{
                    color: var(--narhval-primary);
                    font-weight: 600;
                }}

                em {{
                    color: var(--narhval-teal);
                }}

                /* Links */
                a {{
                    color: var(--narhval-teal);
                    text-decoration: none;
                    font-weight: 500;
                    border-bottom: 1px solid var(--narhval-teal);
                    transition: all 0.2s ease;
                }}

                a:hover {{
                    color: var(--narhval-primary);
                    border-bottom-color: var(--narhval-accent);
                    background: rgba(254, 176, 152, 0.1);
                }}

                /* Lists */
                ul, ol {{
                    margin: 1rem 0 1rem 2rem;
                    padding: 0;
                }}

                li {{
                    margin: 0.5rem 0;
                    line-height: 1.7;
                }}

                li::marker {{
                    color: var(--narhval-teal);
                    font-weight: 600;
                }}

                /* Code */
                code {{
                    background: rgba(1, 79, 103, 0.05);
                    color: var(--narhval-primary);
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 0.9em;
                    border: 1px solid rgba(1, 79, 103, 0.1);
                }}

                pre {{
                    background: linear-gradient(135deg, rgba(1, 79, 103, 0.03) 0%, rgba(0, 128, 128, 0.03) 100%);
                    border-left: 4px solid var(--narhval-teal);
                    padding: 1.25rem;
                    border-radius: 6px;
                    overflow-x: auto;
                    margin: 1.5rem 0;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                }}

                pre code {{
                    background: none;
                    border: none;
                    padding: 0;
                    color: #333;
                    font-size: 0.95em;
                }}

                /* Tables */
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1.5rem 0;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    border-radius: 8px;
                    overflow: hidden;
                }}

                thead {{
                    background: linear-gradient(135deg, var(--narhval-primary) 0%, var(--narhval-teal) 100%);
                    color: var(--narhval-cream);
                }}

                th {{
                    padding: 12px 16px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 0.95rem;
                    letter-spacing: 0.3px;
                }}

                td {{
                    padding: 10px 16px;
                    border-bottom: 1px solid #e0e0e0;
                }}

                tbody tr:nth-child(even) {{
                    background: rgba(1, 79, 103, 0.02);
                }}

                tbody tr:hover {{
                    background: rgba(0, 128, 128, 0.05);
                }}

                tbody tr:last-child td {{
                    border-bottom: none;
                }}

                /* Blockquotes */
                blockquote {{
                    border-left: 4px solid var(--narhval-accent);
                    padding: 1rem 1.5rem;
                    margin: 1.5rem 0;
                    background: rgba(254, 176, 152, 0.08);
                    border-radius: 0 6px 6px 0;
                    color: var(--narhval-primary);
                    font-style: italic;
                }}

                blockquote p {{
                    margin: 0.5rem 0;
                }}

                /* Horizontal rule */
                hr {{
                    border: none;
                    height: 3px;
                    background: linear-gradient(90deg, var(--narhval-primary) 0%, var(--narhval-teal) 50%, var(--narhval-accent) 100%);
                    margin: 2rem 0;
                    border-radius: 2px;
                }}

                /* Images */
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    margin: 1.5rem 0;
                }}

                /* Print styles */
                @media print {{
                    body {{
                        max-width: 100%;
                        padding: 20px;
                    }}

                    h1, h2, h3, h4, h5, h6 {{
                        page-break-after: avoid;
                    }}

                    pre, blockquote, table {{
                        page-break-inside: avoid;
                    }}
                }}

                /* Mobile responsive */
                @media (max-width: 768px) {{
                    body {{
                        padding: 20px 15px;
                    }}

                    h1 {{
                        font-size: 2rem;
                    }}

                    h2 {{
                        font-size: 1.6rem;
                    }}

                    h3 {{
                        font-size: 1.3rem;
                    }}

                    table {{
                        font-size: 0.9rem;
                    }}

                    th, td {{
                        padding: 8px 10px;
                    }}
                }}
        """

    return f"""
    <html>
        <head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <title>Narhval Document</title>
            <style>
                {css_content}
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
    filename_stem = Path(file.filename).stem or "document"

    if export_format == "html":
        html_content = convert_markdown_to_html(content, for_pdf=False)
        html_bytes = html_content.encode("utf-8")
        return send_file(
            BytesIO(html_bytes),
            mimetype="text/html",
            as_attachment=True,
            download_name=f"{filename_stem}.html",
        )

    # For PDF, use direct hex values instead of CSS variables
    html_content = convert_markdown_to_html(content, for_pdf=True)
    pdf_bytes = html_to_pdf_bytes(html_content)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{filename_stem}.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
