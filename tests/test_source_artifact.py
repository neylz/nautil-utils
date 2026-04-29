from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib.util
import unittest
import zipfile


_ARTIFACT_SOURCE_FILE = Path(__file__).resolve().parents[1] / "nautil_utils" / "source" / "artifact.py"
_SPEC = importlib.util.spec_from_file_location("nautil_utils_source_artifact", _ARTIFACT_SOURCE_FILE)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
ArtifactSource = _MODULE.ArtifactSource


class TestArtifactSource(unittest.TestCase):
    def test_copy_files_uses_root_for_directory_copy(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp)

            (src / "include").mkdir()
            (src / "include" / "inside.txt").write_text("ok", encoding="utf-8")
            (src / "outside.txt").write_text("no", encoding="utf-8")

            artifact = SimpleNamespace(path=src)
            ArtifactSource(artifact, root="include").copy_files(dest, ".")

            self.assertTrue((dest / "inside.txt").exists())
            self.assertFalse((dest / "outside.txt").exists())

    def test_copy_files_uses_root_for_archive(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as out_tmp, TemporaryDirectory() as extract_tmp:
            src = Path(src_tmp)
            out_dir = Path(out_tmp)
            extract_dir = Path(extract_tmp)

            (src / "include").mkdir()
            (src / "include" / "inside.txt").write_text("ok", encoding="utf-8")
            (src / "outside.txt").write_text("no", encoding="utf-8")

            artifact = SimpleNamespace(path=src)
            archive_dest = out_dir / "artifact_copy"
            ArtifactSource(artifact, root="include", compressed_format="zip").copy_files(archive_dest, ".")

            archive_path = out_dir / "artifact_copy.zip"
            self.assertTrue(archive_path.exists())

            with zipfile.ZipFile(archive_path, "r") as zf:
                names = zf.namelist()

            self.assertIn("inside.txt", names)
            self.assertNotIn("outside.txt", names)

            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(extract_dir)

            self.assertTrue((extract_dir / "inside.txt").exists())
            self.assertFalse((extract_dir / "outside.txt").exists())

    def test_copy_files_raises_for_missing_root(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            artifact = SimpleNamespace(path=src)

            with self.assertRaises(ValueError):
                ArtifactSource(artifact, root="missing").copy_files(Path(dest_tmp), ".")

    def test_copy_files_copies_directory_from_src_path(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp)

            (src / "nested").mkdir()
            (src / "nested" / "inside.txt").write_text("ok", encoding="utf-8")
            (src / "other.txt").write_text("no", encoding="utf-8")

            artifact = SimpleNamespace(path=src)
            ArtifactSource(artifact).copy_files(dest, "nested")

            self.assertTrue((dest / "inside.txt").exists())
            self.assertFalse((dest / "other.txt").exists())

    def test_copy_files_copies_file_from_src_path(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as dest_tmp:
            src = Path(src_tmp)
            dest = Path(dest_tmp) / "renamed.txt"

            (src / "nested").mkdir()
            (src / "nested" / "inside.txt").write_text("ok", encoding="utf-8")

            artifact = SimpleNamespace(path=src)
            ArtifactSource(artifact).copy_files(dest, "nested/inside.txt")

            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_text(encoding="utf-8"), "ok")

    def test_copy_files_respects_overwrite_for_archives(self):
        with TemporaryDirectory() as src_tmp, TemporaryDirectory() as out_tmp:
            src = Path(src_tmp)
            out_dir = Path(out_tmp)

            (src / "nested").mkdir()
            (src / "nested" / "inside.txt").write_text("ok", encoding="utf-8")

            artifact = SimpleNamespace(path=src)
            archive_dest = out_dir / "artifact_copy"
            existing_archive = out_dir / "artifact_copy.zip"
            existing_archive.write_text("old", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                ArtifactSource(artifact, compressed_format="zip").copy_files(archive_dest, "nested")

            ArtifactSource(artifact, compressed_format="zip").copy_files(archive_dest, "nested", overwrite=True)

            self.assertTrue(existing_archive.exists())
            self.assertGreater(existing_archive.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
