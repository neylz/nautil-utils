from os import PathLike
import shutil

from nautil.core import Artifact, Source

_SUPPORTED_COMPRESSED_FORMATS = {
    "zip": ".zip",
    "tar": ".tar",
    "gztar": ".tar.gz",
}

class ArtifactSource(Source):
    def __init__(self, artifact: Artifact, compressed_format: str = None):
        """
        Creates a source from an existing artifact.

        :param artifact: The artifact to use as a source.
        :param compressed_format: If provided, the artifact will be compressed into the specified format. one of "zip", "tar" or "gztar".

        """
        self.path = artifact.path
        self.compressed_format = compressed_format


    def copy_files(self, dest: PathLike):
        if not self.compressed_format:
            shutil.copytree(self.path, dest, dirs_exist_ok=True)
            return
        
        if self.compressed_format not in _SUPPORTED_COMPRESSED_FORMATS.keys():
            raise ValueError(f"Unsupported compressed format: {self.compressed_format}. Supported formats are: {', '.join(_SUPPORTED_COMPRESSED_FORMATS.keys())}.")
        
        # ensure output has the correct extension
        temp_zip_path = dest if dest.endswith(_SUPPORTED_COMPRESSED_FORMATS[self.compressed_format]) else f"{dest}{_SUPPORTED_COMPRESSED_FORMATS[self.compressed_format]}"
        shutil.make_archive(base_name=temp_zip_path[:-4], format=self.compressed_format, root_dir=self.path)
