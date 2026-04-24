from nautil import Artifact
from nautil_utils.source import GitSource

import nautil_utils.actions

vars = {
    "ARTIFACT": "default",
    "NAME": "example-artifact",
    "VERSION": "1.0.0",
}

src = GitSource(git_url="https://github.com/SurenaStudio/Holiday25-RP", branch="main")

artifact = Artifact(dict(vars, ARTIFACT="main"))\
    .use(src)\
    .json_minify()\
    .output()\
    .output(name="$NAME-$VERSION.zip")\
    .output(name="$NAME", format=Artifact.OutputFormat.DIRECTORY)