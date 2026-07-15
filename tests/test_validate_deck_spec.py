import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "group-meeting-ppt-skill" / "scripts" / "validate_deck_spec.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_deck_spec", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateDeckSpecTest(unittest.TestCase):
    def test_valid_spec_requires_real_figure_asset_and_audience_deck_sections(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "figure.png"
            asset.write_bytes(b"not-a-real-image-but-an-existing-asset")
            spec = {
                "paper": {"title": "Example paper", "citation": "Example et al. (2026)"},
                "meeting": {"duration_minutes": 12, "target_seconds": 660},
                "slides": [
                    {"type": "title", "title": "Example", "source": "PDF p. 1", "estimated_seconds": 20},
                    {"type": "narrative", "title": "Question", "source": "PDF p. 1", "estimated_seconds": 80},
                    {"type": "method", "title": "Method", "source": "PDF p. 2", "estimated_seconds": 120},
                    {"type": "figure", "title": "Fig. 1｜Result", "asset": "figure.png", "figure_label": "Fig. 1", "panel_scope": "Fig. 1a", "pdf_page": 3, "caveat": "Scope", "crop_review": {"named_panel_matches": True, "axes_and_legend_legible": True, "article_prose_removed": True}, "source": "PDF p. 3", "estimated_seconds": 120, "image_aspect": 1.6},
                    {"type": "synthesis", "title": "Conclusion", "source": "PDF p. 4", "estimated_seconds": 120},
                    {"type": "questions", "title": "Questions", "source": "PDF p. 4", "estimated_seconds": 120},
                ],
            }
            self.assertEqual(module.validate(spec, root), [])

    def test_internal_production_copy_rejects_the_spec(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = {
                "paper": {"title": "Example paper", "citation": "Example et al. (2026)"},
                "meeting": {"duration_minutes": 12, "target_seconds": 660},
                "slides": [
                    {"type": "title", "title": "Example", "source": "PDF p. 1", "estimated_seconds": 20},
                    {"type": "narrative", "title": "这一页目的", "source": "PDF p. 1", "estimated_seconds": 80},
                    {"type": "method", "title": "Method", "source": "PDF p. 2", "estimated_seconds": 120},
                    {"type": "figure", "title": "Fig. 1", "asset": "missing.png", "figure_label": "Fig. 1", "panel_scope": "Fig. 1a", "pdf_page": 3, "caveat": "Scope", "crop_review": {"named_panel_matches": True, "axes_and_legend_legible": True, "article_prose_removed": True}, "source": "PDF p. 3", "estimated_seconds": 120, "image_aspect": 1.6},
                    {"type": "synthesis", "title": "Conclusion", "source": "PDF p. 4", "estimated_seconds": 120},
                    {"type": "questions", "title": "Questions", "source": "PDF p. 4", "estimated_seconds": 120},
                ],
            }
            errors = module.validate(spec, root)
            self.assertTrue(any("forbidden internal copy" in error for error in errors))
            self.assertTrue(any("figure asset does not exist" in error for error in errors))

    def test_figure_requires_a_reviewed_clean_panel_crop(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "figure.png"
            asset.write_bytes(b"existing")
            spec = {
                "paper": {"title": "Example paper", "citation": "Example et al. (2026)"},
                "meeting": {"duration_minutes": 12, "target_seconds": 660},
                "slides": [
                    {"type": "title", "title": "Example", "source": "PDF p. 1", "estimated_seconds": 20},
                    {"type": "narrative", "title": "Question", "source": "PDF p. 1", "estimated_seconds": 80},
                    {"type": "method", "title": "Method", "source": "PDF p. 2", "estimated_seconds": 120},
                    {"type": "figure", "title": "Fig. 1｜Result", "asset": "figure.png", "figure_label": "Fig. 1", "panel_scope": "Fig. 1a", "pdf_page": 3, "caveat": "Scope", "crop_review": {"named_panel_matches": True, "axes_and_legend_legible": True, "article_prose_removed": False}, "source": "PDF p. 3", "estimated_seconds": 120, "image_aspect": 1.6},
                    {"type": "synthesis", "title": "Conclusion", "source": "PDF p. 4", "estimated_seconds": 120},
                    {"type": "questions", "title": "Questions", "source": "PDF p. 4", "estimated_seconds": 120},
                ],
            }
            errors = module.validate(spec, root)
            self.assertTrue(any("crop_review.article_prose_removed" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
