import json
import os

from nautil.plugin import action
from nautil import Artifact


@action("json_minify")
def json_minify(artifact: Artifact, remove_spaces=True):
    """
    Minifies JSON files in the artifact's workspace by removing unnecessary whitespace.

    @param remove_spaces: Whether to have spaces or not between separators "," and ":" (default: True).
    """
    
    def step(workspace):
        artifact.log("json_minify(remove_spaces={})".format(remove_spaces))

        for root, dirs, files in os.walk(workspace):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            artifact.log(f"\tWarning: Invalid JSON in file '{file_path}'. Skipping.")
                            continue
                    
                    with open(file_path, "w") as f:
                        if remove_spaces:
                            json.dump(data, f, separators=(",", ":"))
                        else:
                            json.dump(data, f)

    return step