#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерация қазақша аудио файлдары (edge-tts, kk-KZ-AigulNeural).
Шығатын нәрселер:
  /home/shakan/til/audio/NNNN.mp3
  /home/shakan/til/audio/manifest.json  -> { "Сөз": "NNNN.mp3", ... }
"""
import json, os, re, asyncio, sys

os.chdir("/home/shakan/til")
os.makedirs("audio", exist_ok=True)

html = open("index.html", encoding="utf-8").read()

# --- WORDS: word:"..." өрістерін алу (WORDS массивінің аясында) ---
words_section = html.split("const WORDS = [")[1].split("];")[0]
words = re.findall(r'word:"((?:[^"\\]|\\.)*)"', words_section)
# уникалді, ретін сақтай отырып
seen, uniq_words = set(), []
for w in words:
    if w not in seen:
        seen.add(w)
        uniq_words.append(w)

# --- PROVERBS: t:"..." алу ---
prov_section = html.split("const PROVERBS = [")[1].split("];")[0]
proverbs = re.findall(r'\{t:"((?:[^"\\]|\\.)*)"', prov_section)

# --- Оқу тақырыптары ---
read_titles = ["Қазақ даласындағы күн", "Білімнің құндылығы"]

# Тізім: (text_for_tts, key_in_manifest)
items = []
for w in uniq_words:
    tts_text = w.replace(" / ", ", ")   # "Ана / Шеше" -> "Ана, Шеше"
    items.append((tts_text, w))
for p in proverbs:
    items.append((p, "prov:" + p))
for t in read_titles:
    items.append((t, "read:" + t))

import edge_tts

async def gen(idx, text, key, sem):
    fname = f"{idx:04d}.mp3"
    path = os.path.join("audio", fname)
    async with sem:
        for attempt in range(3):
            try:
                tts = edge_tts.Communicate(text, "kk-KZ-AigulNeural", rate="-10%")
                await tts.save(path)
                if os.path.exists(path) and os.path.getsize(path) > 500:
                    return key, fname
                else:
                    raise RuntimeError("file too small")
            except Exception as e:
                if attempt == 2:
                    print(f"FAIL {key!r}: {e}", file=sys.stderr)
                    return None
                await asyncio.sleep(1.5)

async def main():
    sem = asyncio.Semaphore(4)
    manifest = {}
    idx = 1
    tasks = []
    for text, key in items:
        tasks.append(gen(idx, text, key, sem))
        idx += 1
    results = await asyncio.gather(*tasks)
    for r in results:
        if r:
            manifest[r[0]] = r[1]
    with open("audio/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    ok = sum(1 for r in results if r)
    print(f"Done: {ok}/{len(items)} аудио жасалды")

asyncio.run(main())
