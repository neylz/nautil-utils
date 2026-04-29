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

            LocalSource(src).copy_files(dest, ".")

            self.assertTrue((dest / "level.dat").exists())
            self.assertEqual((dest / "already_there.txt").read_text(encoding="utf-8"), "keep")

    def test_copy_files_copies_directory_from_src_path(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp)

            (src / "sub").mkdir()
            (src / "sub" / "inside.txt").write_text("ok", encoding="utf-8")
            (src / "outside.txt").write_text("no", encoding="utf-8")

            LocalSource(src).copy_files(dest, "sub")

            self.assertTrue((dest / "inside.txt").exists())
            self.assertFalse((dest / "outside.txt").exists())

    def test_copy_files_copies_file_from_src_path(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp) / "renamed.txt"

            (src / "nested").mkdir()
            (src / "nested" / "data.txt").write_text("content", encoding="utf-8")

            LocalSource(src).copy_files(dest, "nested/data.txt")

            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_text(encoding="utf-8"), "content")

    def test_copy_files_respects_overwrite_for_files(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp) / "data.txt"

            (src / "nested").mkdir()
            (src / "nested" / "data.txt").write_text("new", encoding="utf-8")
            dest.write_text("old", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                LocalSource(src).copy_files(dest, "nested/data.txt")

            LocalSource(src).copy_files(dest, "nested/data.txt", overwrite=True)

            self.assertEqual(dest.read_text(encoding="utf-8"), "new")


if __name__ == "__main__":
    unittest.main()
