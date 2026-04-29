from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from nautil_utils.actions.foreach import foreach


class TestForeachAction(unittest.TestCase):
    def test_foreach_calls_direct_callback_for_matching_files(self):
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "keep.txt").write_text("1", encoding="utf-8")
            (workspace / "skip.md").write_text("1", encoding="utf-8")

            seen = []

            step = foreach(
                None,
                lambda file_name, _file_path, _workspace: file_name.endswith(".txt"),
                lambda rel_path, _workspace: seen.append(rel_path),
            )

            step(str(workspace))

            self.assertEqual(seen, ["keep.txt"])

    def test_foreach_supports_action_factory_returning_step(self):
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "a.txt").write_text("1", encoding="utf-8")
            (workspace / "b.txt").write_text("1", encoding="utf-8")

            seen = []

            def item_action(rel_path: str):
                def per_item_step(_workspace: str):
                    seen.append(rel_path)

                return per_item_step

            step = foreach(
                None,
                lambda file_name, _file_path, _workspace: file_name.endswith(".txt"),
                item_action,
            )

            step(str(workspace))

            self.assertCountEqual(seen, ["a.txt", "b.txt"])

    def test_foreach_non_recursive_only_processes_top_level(self):
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "top.txt").write_text("1", encoding="utf-8")
            (workspace / "nested").mkdir()
            (workspace / "nested" / "deep.txt").write_text("1", encoding="utf-8")

            seen = []

            step = foreach(
                None,
                lambda file_name, _file_path, _workspace: file_name.endswith(".txt"),
                lambda rel_path, _workspace: seen.append(rel_path),
                recursive=False,
            )

            step(str(workspace))

            self.assertEqual(seen, ["top.txt"])

    def test_foreach_item_action_can_use_name_and_path_signature(self):
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "datapacks").mkdir()
            (workspace / "datapacks" / "pack.zip").write_text("1", encoding="utf-8")

            seen = []

            step = foreach(
                None,
                lambda _name, _path, _workspace: True,
                lambda file_name, file_path: seen.append((file_name, file_path)),
                root="datapacks",
                recursive=False,
            )

            step(str(workspace))

            self.assertEqual(seen, [("pack.zip", "datapacks/")])


if __name__ == "__main__":
    unittest.main()
