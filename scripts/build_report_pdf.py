"""
Convertit reports/HR_Analytics_Report.md en PDF professionnel.
Usage : python scripts/build_report_pdf.py
"""
from pathlib import Path
import markdown
from xhtml2pdf import pisa

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "reports" / "HR_Analytics_Report.md"
PDF = ROOT / "reports" / "HR_Analytics_Report.pdf"
REPORTS_DIR = ROOT / "reports"

CSS = """
@page { size: A4; margin: 1.6cm 1.8cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5px; color: #222; line-height: 1.45; }
h1 { color: #1B3A4B; font-size: 22px; border-bottom: 3px solid #2E86AB; padding-bottom: 4px; }
h2 { color: #2E86AB; font-size: 16px; margin-top: 16px; border-bottom: 1px solid #ddd; padding-bottom: 2px; }
h3 { color: #1B3A4B; font-size: 13px; margin-top: 12px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.5px; }
th { background: #2E86AB; color: white; padding: 5px 7px; text-align: left; }
td { border: 1px solid #cfd8dc; padding: 4px 7px; }
tr:nth-child(even) td { background: #f4f8fb; }
img { max-width: 95%; margin: 6px 0; }
blockquote { background: #fff6f0; border-left: 4px solid #E4572E; margin: 8px 0; padding: 6px 10px; color: #444; }
code { background: #eef2f5; padding: 1px 3px; font-family: Consolas, monospace; }
hr { border: none; border-top: 1px solid #ddd; margin: 12px 0; }
strong { color: #1B3A4B; }
"""

def link_callback(uri, rel):
    """Résout les chemins d'images relatifs (figures/...) en chemins absolus."""
    p = (REPORTS_DIR / uri).resolve()
    return str(p)

def main():
    text = MD.read_text(encoding="utf-8")
    html_body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    with open(PDF, "wb") as f:
        status = pisa.CreatePDF(html, dest=f, link_callback=link_callback, encoding="utf-8")
    if status.err:
        raise SystemExit(f"Erreur de génération PDF ({status.err})")
    print("PDF généré :", PDF, f"({PDF.stat().st_size//1024} Ko)")

if __name__ == "__main__":
    main()
