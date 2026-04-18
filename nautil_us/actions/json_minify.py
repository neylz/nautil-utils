import json
import os

from nautil.plugin import action
from nautil import Artifact


@action("json_minify")
def json_minify(artifact: Artifact, remove_spaces=True):
    
    def step(workspace):
        print("json_minify")

        for root, dirs, files in os.walk(workspace):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            continue # skip invalid json
                    
                    with open(file_path, "w") as f:
                        if remove_spaces:
                            json.dump(data, f, separators=(",", ":"))
                        else:
                            json.dump(data, f)

    return step