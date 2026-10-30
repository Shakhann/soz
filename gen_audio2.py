#!/usr/bin/env python3
"""ДАСТАН: барлық аудио қайта генерация (edge-tts, kk-KZ-AigulNeural).
Сөздер + мақал-мәтелдер + жаңылтпаштар + жырлар + аңыздар + тағамдар + киімдер + тарих + ою.
"""
import json, os, asyncio, sys, re

os.chdir("/home/shakan/til")
os.makedirs("audio", exist_ok=True)

# Ескі mp3-ті өшіру
for f in os.listdir("audio"):
    if f.endswith(".mp3"):
        os.remove(os.path.join("audio", f))
print("Ескі mp3-ті өшірілді")

# --- index.html-ден WORDS алу ---
html = open("index.html", encoding="utf-8").read()

words_section = html.split("const WORDS = [")[1].split("];")[0]
words = re.findall(r'word:"((?:[^"\\]|\\.)*)"', words_section)
seen, uniq_words = set(), []
for w in words:
    if w not in seen:
        seen.add(w)
        uniq_words.append(w)
print(f"Сөздер: {len(uniq_words)}")

# --- content-a.js-ден PROVERBS + TONGUES алу ---
ca = open("content-a.js", encoding="utf-8").read()
proverbs = re.findall(r't:"((?:[^"\\]|\\.)*)"', ca.split("PROVERBS: [")[1].split("],\n")[0])
print(f"Мақал-мәтелдер: {len(proverbs)}")

tongues = re.findall(r't:"((?:[^"\\]|\\.)*)"', ca.split("TONGUES: [")[1].split("];")[0])
print(f"Жаңылтпаштар: {len(tongues)}")

# --- content-b.js-ден FOODS, CLOTHES, LEGENDS, ORNAMENTS алу ---
cb = open("content-b.js", encoding="utf-8").read()
foods = re.findall(r't:"((?:[^"\\]|\\.)*)"', cb.split("FOODS: [")[1].split("],\n")[0])
print(f"Тағамдар: {len(foods)}")
clothes = re.findall(r't:"((?:[^"\\]|\\.)*)"', cb.split("CLOTHES: [")[1].split("],\n")[0])
print(f"Киімдер: {len(clothes)}")
legends = re.findall(r't:"((?:[^"\\]|\\.)*)"', cb.split("LEGENDS: [")[1].split("],\n")[0])
print(f"Аңыздар: {len(legends)}")

# --- content-c.js-ден HISTORY, JYRS алу ---
cc = open("content-c.js", encoding="utf-8").read()
history = re.findall(r't:"((?:[^"\\]|\\.)*)"', cc.split("HISTORY: [")[1].split("],\n")[0])
print(f"Тарих сабақтары: {len(history)}")
jyrs = re.findall(r't:"((?:[^"\\]|\\.)*)"', cc.split("JYRS: [")[1].split("];")[0])
print(f"Жыр-дастандар: {len(jyrs)}")

# --- Тізім: (tts_text, key) ---
items = []
for w in uniq_words:
    items.append((w.replace(" / ", ", "), w))
for p in proverbs:
    items.append((p, "prov:" + p))
for t in tongues:
    items.append((t, "tongue:" + t))
for f_ in foods:
    items.append((f_, "food:" + f_))
for c in clothes:
    items.append((c, "cloth:" + c))
for l in legends:
    items.append((l, "legend:" + l))
for h in history:
    items.append((h, "history:" + h))
for j in jyrs:
    items.append((j, "jyr:" + j))

print(f"\nБарлығы: {len(items)} аудио файл")

import edge_tts

VOICE = "kk-KZ-AigulNeural"
RATE = "-5%"

async def gen(idx, text, key, sem):
    fname = f"{idx:04d}.mp3"
    path = os.path.join("audio", fname)
    async with sem:
        for attempt in range(3):
            try:
                tts = edge_tts.Communicate(text, VOICE, rate=RATE)
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
    sem = asyncio.Semaphore(5)
    tasks = [gen(i+1, text, key, sem) for i, (text, key) in enumerate(items)]
    results = await asyncio.gather(*tasks)
    
    manifest = {}
    ok = 0
    for r in results:
        if r:
            key, fname = r
            manifest[key] = fname
            ok += 1
    
    with open("audio/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"\nДайын: {ok}/{len(items)} файл")
    total_size = sum(os.path.getsize(os.path.join("audio", f)) for f in os.listdir("audio") if f.endswith(".mp3"))
    print(f"Барлық өлшем: {total_size/1024/1024:.1f} MB")

asyncio.run(main())
