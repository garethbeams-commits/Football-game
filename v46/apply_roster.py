#!/usr/bin/env python3
"""Expand the checked V45 Android source into a 1,250-player V46 APK.

The two .zlib.b64 files are byte-for-byte compressed versions of the
V46 250-player selected-career records and the V46 builder.
All first-pass additions keep unknown appearance values null.
"""
from pathlib import Path
import base64
import subprocess
import sys
import zlib

root=Path(__file__).resolve().parent.parent
folder=root/"v46"
for file_name,output_name in (
    ("roster.zlib.b64","V46_250_selected_clubs.txt"),
    ("engine.zlib.b64","build_v46.py"),
):
    data=(folder/file_name).read_text(encoding="ascii")
    decoded=zlib.decompress(base64.b64decode("".join(data.splitlines())))
    (folder/output_name).write_bytes(decoded)

subprocess.run([
    sys.executable,str(folder/"build_v46.py"),
    "--html",str(root/"app/src/main/assets/www/index.html"),
    "--candidate-file",str(folder/"V46_250_selected_clubs.txt"),
    "--gradle",str(root/"app/build.gradle"),
    "--audit",str(folder/"V46_250_PLAYER_REVIEW_QUEUE.csv"),
],check=True)
