import os
import tarfile
import zipfile

from nautil.plugin import action
from nautil import Artifact


def _resolve_path(workspace: str, value: str) -> str:
    full_path = value if os.path.isabs(value) else os.path.join(workspace, value)
    return os.path.normpath(full_path)


@action("archive")
def archive(artifact: Artifact, source_path: str, output_path: str, archive_format: str = "zip", overwrite: bool = True):

    def step(workspace: str):
        print(f"archive({source_path} -> {output_path}, format={archive_format})")

        source_full_path = _resolve_path(workspace, source_path)
        output_full_path = _resolve_path(workspace, output_path)

        if not os.path.exists(source_full_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")

        parent_dir = os.path.dirname(output_full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        if os.path.exists(output_full_path):
            if not overwrite:
                raise FileExistsError(f"Archive already exists: {output_path}")
            os.remove(output_full_path)

        source_name = os.path.basename(source_full_path)
        source_parent = os.path.dirname(source_full_path)

        if archive_format == "zip":
            with zipfile.ZipFile(output_full_path, "w", compression=zipfile.ZIP_DEFLATED) as archive_file:
                if os.path.isdir(source_full_path):
                    for root, _, files in os.walk(source_full_path):
                        for file_name in files:
                            full_file = os.path.join(root, file_name)
                            arcname = os.path.relpath(full_file, source_parent)
                            archive_file.write(full_file, arcname)
                else:
                    archive_file.write(source_full_path, source_name)
            return

        tar_modes = {
            "tar": "w",
            "gztar": "w:gz",
            "bztar": "w:bz2",
            "xztar": "w:xz",
        }

        if archive_format in tar_modes:
            with tarfile.open(output_full_path, tar_modes[archive_format]) as archive_file:
                archive_file.add(source_full_path, arcname=source_name)
            return

        raise ValueError("Unsupported archive format. Use one of: zip, tar, gztar, bztar, xztar")

    return step
