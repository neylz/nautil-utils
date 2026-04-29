import json
from os import PathLike
from pathlib import Path

from nautil.plugin import action
from nautil import Artifact


@action("json_set")
def json_set(artifact: Artifact, file: PathLike, key: str, value: object):
    """
    Sets a value in JSON files in the artifact's workspace.

    @param file: The path to the JSON file.
    @param key: The key to set. Supports nested keys and array indices using dot notation (e.g. "parent.child[0].key").
    @param value: The value to set. Must be JSON-serializable.
    """
    
    def step(workspace):
        _file = artifact.parset(file)
        _key = artifact.parset(key)
        _value = artifact.parset(value) if isinstance(value, str) else value

        artifact.log("json_set(file={}, key={}, value={})".format(_file, _key, _value))

        file_path = Path(workspace) / _file

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        keys = _key.split('.')
        current = data
        
        for i, k in enumerate(keys[:-1]):
            # parse array indices
            if '[' in k:
                key_name = k[:k.index('[')]
                index_str = k[k.index('[') + 1:k.index(']')]
                index = int(index_str)
                current = current[key_name][index]
            else:
                if k not in current:
                    current[k] = {}
                current = current[k]
        
        # set
        final_key = keys[-1]
        if '[' in final_key:
            key_name = final_key[:final_key.index('[')]
            index_str = final_key[final_key.index('[') + 1:final_key.index(']')]
            index = int(index_str)
            current[key_name][index] = _value
        else:
            current[final_key] = _value
        
        # Write back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    return step