from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import unittest

import git


_GIT_SOURCE_FILE = Path(__file__).resolve().parents[1] / "nautil_utils" / "source" / "git.py"
_SPEC = importlib.util.spec_from_file_location("nautil_utils_source_git", _GIT_SOURCE_FILE)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
GitSource = _MODULE.GitSource


class TestGitSource(unittest.TestCase):
    def test_copy_files_copies_directory_from_src_path(self):
        with TemporaryDirectory() as repo_tmp, TemporaryDirectory() as dest_tmp:
            repo_path = Path(repo_tmp)
            dest = Path(dest_tmp)

            (repo_path / "nested").mkdir()
            (repo_path / "nested" / "inside.txt").write_text("ok", encoding="utf-8")
            (repo_path / "outside.txt").write_text("no", encoding="utf-8")

            repo = git.Repo.init(repo_path, initial_branch="main")
            repo.index.add(["nested/inside.txt", "outside.txt"])
            repo.index.commit("initial")
            repo.close()

            GitSource(str(repo_path), branch="main").copy_files(dest, "nested")

            self.assertTrue((dest / "inside.txt").exists())
            self.assertFalse((dest / "outside.txt").exists())
            self.assertFalse((dest / ".git").exists())

    def test_copy_files_copies_file_from_src_path(self):
        with TemporaryDirectory() as repo_tmp, TemporaryDirectory() as dest_tmp:
            repo_path = Path(repo_tmp)
            dest = Path(dest_tmp) / "renamed.txt"

            (repo_path / "nested").mkdir()
            (repo_path / "nested" / "inside.txt").write_text("ok", encoding="utf-8")

            repo = git.Repo.init(repo_path, initial_branch="main")
            repo.index.add(["nested/inside.txt"])
            repo.index.commit("initial")
            repo.close()

            GitSource(str(repo_path), branch="main").copy_files(dest, "nested/inside.txt")

            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_text(encoding="utf-8"), "ok")

    def test_copy_files_respects_overwrite_for_files(self):
        with TemporaryDirectory() as repo_tmp, TemporaryDirectory() as dest_tmp:
            repo_path = Path(repo_tmp)
            dest = Path(dest_tmp) / "inside.txt"

            (repo_path / "nested").mkdir()
            (repo_path / "nested" / "inside.txt").write_text("new", encoding="utf-8")

            repo = git.Repo.init(repo_path, initial_branch="main")
            repo.index.add(["nested/inside.txt"])
            repo.index.commit("initial")
            repo.close()

            dest.write_text("old", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                GitSource(str(repo_path), branch="main").copy_files(dest, "nested/inside.txt")

            GitSource(str(repo_path), branch="main").copy_files(dest, "nested/inside.txt", overwrite=True)

            self.assertEqual(dest.read_text(encoding="utf-8"), "new")


if __name__ == "__main__":
    unittest.main()
