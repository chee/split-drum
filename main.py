#!/usr/bin/env python3
from json import loads as parse_json
from sys import argv
from pathlib import Path
from ffmpeg import FFmpeg
from chunk import Chunk
import asyncio

def get_aif_json(path):
	aif = open(path, "rb")
	# i don't care about the first 12 bytes
	aif.read(12)
	for _ in range(10):
		try:
			chunk = Chunk(aif)
			if chunk.getname() == b'APPL':
				header = chunk.read(4)
				if header == b'op-1':
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
target_dir = "."
if len(argv) > 2:
	target_dir = argv[2]
	json = get_aif_json(aif)
	samples = []

Path(target_dir).mkdir(parents=True, exist_ok=True)

loop = asyncio.get_event_loop()
for index in range(len(json['start'])):
	start = json['start'][index] / 4096 / 44100
	end = json['end'][index] / 4096 / 44100
	loop.run_until_complete(FFmpeg().option('y').input(aif).output(
		f"{target_dir}/{index:02d}.wav",
		ss=(start),
		to=(end)
	).execute())

loop.close
