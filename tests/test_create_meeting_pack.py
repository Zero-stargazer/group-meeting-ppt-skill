import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "group-meeting-ppt-skill" / "scripts" / "create_meeting_pack.py"
SAMPLE = ROOT / "examples" / "sample-paper-input.json"


class CreateMeetingPackTest(unittest.TestCase):
    def test_create_meeting_pack_generates_required_markdown_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(SAMPLE), "--outdir", str(outdir)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            required = [
                "meeting_outline.md",
                "slide_plan.md",
                "advisor_questions.md",
                "integrity_checklist.md",
            ]
            for name in required:
                self.assertTrue((outdir / name).exists(), f"missing {name}")

            outline = (outdir / "meeting_outline.md").read_text(encoding="utf-8")
            slide_plan = (outdir / "slide_plan.md").read_text(encoding="utf-8")
            questions = (outdir / "advisor_questions.md").read_text(encoding="utf-8")
            integrity = (outdir / "integrity_checklist.md").read_text(encoding="utf-8")

            self.assertIn("10页组会PPT大纲", outline)
            self.assertIn("数字微流控与多重核酸检测", outline)
            self.assertIn("Slide 01", slide_plan)
            self.assertIn("Slide 10", slide_plan)
            self.assertIn("老师可能追问", questions)
            self.assertIn("这个方法为什么可靠", questions)
            self.assertIn("不编造", integrity)
            self.assertIn("关键数据必须回到原文核对", integrity)


if __name__ == "__main__":
    unittest.main()
