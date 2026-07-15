import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "group-meeting-ppt-skill" / "scripts" / "render_pdf_figure_assets.py"


class RenderPdfFigureAssetsTest(unittest.TestCase):
    def test_caption_page_renders_a_real_source_page_and_manifest(self):
        for package in ["reportlab", "pdfplumber"]:
            if importlib.util.find_spec(package) is None:
                self.skipTest(f"{package} is not installed in this Python environment")

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf = root / "paper.pdf"
            notes = root / "paper.notes.json"
            outdir = root / "assets"
            c = canvas.Canvas(str(pdf), pagesize=letter)
            c.drawString(72, 700, "Fig. 1 | Test workflow")
            c.rect(72, 450, 360, 180, fill=0)
            c.drawString(72, 420, "Figure caption text")
            c.save()
            notes.write_text(
                json.dumps({"figures_to_discuss": [{"label": "Fig. 1", "why_use": "test"}]}, ensure_ascii=False),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--pdf", str(pdf), "--notes", str(notes), "--outdir", str(outdir)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((outdir / "figure-assets.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["figure_assets"]), 1)
            rendered = Path(manifest["figure_assets"][0]["asset"])
            self.assertTrue(rendered.exists())
            self.assertGreater(rendered.stat().st_size, 1_000)


if __name__ == "__main__":
    unittest.main()
