from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import unittest


_LOCAL_SOURCE_FILE = Path(__file__).resolve().parents[1] / "nautil_utils" / "source" / "local.py"
_SPEC = importlib.util.spec_from_file_location("nautil_utils_source_local", _LOCAL_SOURCE_FILE)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
LocalSource = _MODULE.LocalSource


class TestLocalSource(unittest.TestCase):
    def test_copy_files_allows_existing_destination(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp)

            (src / "level.dat").write_text("map-data", encoding="utf-8")
            (dest / "already_there.txt").write_text("keep", encoding="utf-8")

            LocalSource(src).copy_files(dest)

            self.assertTrue((dest / "level.dat").exists())
            self.assertEqual((dest / "already_there.txt").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
