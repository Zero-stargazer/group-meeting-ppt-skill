import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "group-meeting-ppt-skill" / "scripts" / "create_pptx_from_pdf.py"


def write_sample_pdf(path: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    lines = [
        "A Rapid Multiplex Assay for Pathogen Detection",
        "Abstract",
        "This paper presents a multiplex rapid assay that combines target amplification,",
        "spatial encoding, and fluorescence readout for low-resource pathogen detection.",
        "The method aims to reduce workflow complexity when symptoms overlap.",
        "Introduction",
        "Single-target assays are inefficient for co-infection scenarios and require repeated testing.",
        "Materials and Methods",
        "The authors designed primer sets, mapped targets to spatial codes, captured fluorescence,",
        "and used threshold rules to call positive reactions.",
        "Results",
        "The assay distinguished multiple targets in a single workflow. The encoded readout reduced",
        "interpretation complexity and worked on simulated samples.",
        "Figure 1. Overall workflow from sample input to encoded fluorescence readout.",
        "Figure 2. Primer screening and target design strategy.",
        "Discussion",
        "The sample size is limited and clinical generalization requires further validation.",
    ]
    y = height - 72
    for line in lines:
        c.drawString(72, y, line)
        y -= 22
        if y < 72:
            c.showPage()
            y = height - 72
    c.save()


class CreatePptxFromPdfTest(unittest.TestCase):
    def test_create_pptx_from_pdf_generates_notes_json_and_ten_slide_deck(self):
        for package in ["reportlab", "pdfplumber", "pptx"]:
            if importlib.util.find_spec(package) is None:
                self.skipTest(f"{package} is not installed in this Python environment")

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            pdf = tmpdir / "sample-paper.pdf"
            notes = tmpdir / "sample-paper.notes.json"
            pptx = tmpdir / "sample-paper.pptx"
            write_sample_pdf(pdf)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pdf",
                    str(pdf),
                    "--out",
                    str(pptx),
                    "--notes-json",
                    str(notes),
                    "--research-direction",
                    "数字微流控与多重核酸检测",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(notes.exists())
            self.assertTrue(pptx.exists())

            data = json.loads(notes.read_text(encoding="utf-8"))
            self.assertIn("Rapid Multiplex Assay", data["paper_title_en"])
            self.assertEqual(data["research_direction"], "数字微流控与多重核酸检测")
            self.assertGreaterEqual(len(data["method_route"]), 2)
            self.assertGreaterEqual(len(data["figures_to_discuss"]), 2)

            from pptx import Presentation

            deck = Presentation(pptx)
            self.assertEqual(len(deck.slides), 10)


if __name__ == "__main__":
    unittest.main()
