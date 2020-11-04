#!/usr/bin/env python3
from json import loads as parse_json
from chunk import Chunk
from sys import argv
from pathlib import Path
from ffmpeg import FFmpeg
import asyncio

def get_aif_json(path):
    aif = open(path, "rb")
    data = aif.read(4)
    if data != b'FORM':
        aif.close()
        return None
    data = aif.read(4)
    data = aif.read(4)
    if data != b'AIFF' and data != b'AIFC':
        aif.close()
        return None
    for _ in range(10):
        try:
            chunk = Chunk(aif)
            if chunk.getname() == b'APPL':
                data = chunk.read(4)
                if data == b'op-1':
                    json = parse_json(
                        chunk.read(
                            chunk.getsize() - 4
                        ).decode('utf-8').strip('\0').strip()
                    )
                    aif.close()
                    return json
            chunk.skip()
        except EOFError:
            aif.close()
            return None
aif = argv[1]
target_dir = argv[2] or "."
json = get_aif_json(aif)
samples = []

Path(target_dir).mkdir(parents=True, exist_ok=True)

loop = asyncio.get_event_loop()
for index in range(len(json['start'])):
    start = json['start'][index] / 41000 / 4096
    end = json['end'][index] / 41000 / 4096
    loop.run_until_complete(FFmpeg().option('y').input(aif).output(
        f"{target_dir}/{index}.wav",
        ss=start,
        to=end
    ).execute())

loop.close
