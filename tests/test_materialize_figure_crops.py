import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "group-meeting-ppt-skill" / "scripts" / "materialize_figure_crops.py"


def load_module():
    spec = importlib.util.spec_from_file_location("materialize_figure_crops", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MaterializeFigureCropsTest(unittest.TestCase):
    def test_crop_box_becomes_a_real_png_and_is_removed_from_private_spec(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            Image.new("RGB", (100, 80), (220, 40, 20)).save(source)
            spec_path = root / "deck-spec.json"
            spec_path.write_text(json.dumps({"slides": [{"type": "figure", "asset": "source.png", "crop_box": {"left": 0.10, "top": 0.25, "right": 0.20, "bottom": 0.25}}]}), encoding="utf-8")
            self.assertEqual(module.materialize(spec_path, root / "crops"), 1)
            result = json.loads(spec_path.read_text(encoding="utf-8"))
            item = result["slides"][0]
            self.assertNotIn("crop_box", item)
            self.assertTrue(Path(item["asset"]).exists())
            self.assertEqual(item["image_aspect"], 1.75)
            with Image.open(item["asset"]) as crop:
                self.assertEqual(crop.size, (70, 40))

    def test_focused_panel_crop_is_allowed_when_the_panel_is_smaller_than_one_fifth_of_a_page(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            Image.new("RGB", (200, 200), (30, 120, 200)).save(source)
            spec_path = root / "deck-spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "slides": [
                            {
                                "type": "figure",
                                "asset": "source.png",
                                "crop_box": {"left": 0.40, "top": 0.42, "right": 0.42, "bottom": 0.40},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(module.materialize(spec_path, root / "crops"), 1)
            result = json.loads(spec_path.read_text(encoding="utf-8"))
            self.assertAlmostEqual(result["slides"][0]["image_aspect"], 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
