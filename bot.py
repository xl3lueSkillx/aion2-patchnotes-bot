import json, os, re, time, html
from pathlib import Path
import requests
from deep_translator import GoogleTranslator

APP_ID = 3393110
STATE = Path('seen.json')
API = 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/'
WEBHOOK = os.environ.get('DISCORD_WEBHOOK_URL', '')
HEADERS = {'User-Agent': 'AION2-Discord-Patchnotes/1.0'}

def eligible(title):
    return bool(re.search(r'patch\s*notes?|patchnotes?|hot\s*fix(?:es)?|patchnotizen|패치\s*노트|핫픽스', title, re.I))

def clean_bbcode(value):
    value = re.sub(r'\[url=(.*?)\](.*?)\[/url\]', r'\2 (\1)', value, flags=re.I|re.S)
    value = re.sub(r'\[/?[^\]]+\]', '', value)
    value = re.sub(r'(?m)^\s*\{STEAM_CLAN_IMAGE\}[^\s]*', '', value)
    value = html.unescape(value)
    value = re.sub(r'\n{3,}', '\n\n', value)
    return value.strip()

def translate(text):
    if not text.strip(): return ''
    translator = GoogleTranslator(source='auto', target='de')
    # Translation service imposes size limits; split at paragraph boundaries.
    chunks, current = [], ''
    for para in text.splitlines():
        if len(para) > 3500:
            parts = [para[i:i+3500] for i in range(0, len(para), 3500)]
        else: parts = [para]
        for part in parts:
            if len(current) + len(part) + 1 > 3500:
                if current: chunks.append(current)
                current = part
            else: current += ('\n' if current else '') + part
    if current: chunks.append(current)
    return '\n'.join(translator.translate(c) or '' for c in chunks)

def send(content):
    response = requests.post(WEBHOOK, json={'username':'AION 2 Patch Notes','content':content,'allowed_mentions':{'parse':[]}}, timeout=30)
    if response.status_code == 429:
        delay = min(float(response.json().get('retry_after', 2)), 30)
        time.sleep(delay)
        response = requests.post(WEBHOOK, json={'username':'AION 2 Patch Notes','content':content,'allowed_mentions':{'parse':[]}}, timeout=30)
    response.raise_for_status()

def split_text(text, limit=1700):
    chunks=[]
    while text:
        if len(text)<=limit:
            chunks.append(text); break
        cut=text.rfind('\n', 0, limit)
        if cut < limit//3: cut=limit
        chunks.append(text[:cut]); text=text[cut:].lstrip('\n')
    return chunks

def main():
    if not WEBHOOK: raise RuntimeError('Missing DISCORD_WEBHOOK_URL secret')
    r=requests.get(API, params={'appid':APP_ID,'count':100,'maxlength':0,'feeds':'steam_community_announcements'}, headers=HEADERS,timeout=30)
    r.raise_for_status()
    entries=r.json()['appnews']['newsitems']
    saved=json.loads(STATE.read_text()) if STATE.exists() else None
    ids={str(x['gid']) for x in entries}
    if saved is None:
        STATE.write_text(json.dumps(sorted(ids),indent=2)+'\n')
        print('Initial run: saved current announcements; nothing posted.')
        return
    seen=set(saved)
    for item in reversed(entries):
        gid=str(item['gid'])
        if gid in seen: continue
        if eligible(item.get('title','')):
            title=clean_bbcode(item.get('title',''))
            body=clean_bbcode(item.get('contents',''))
            try:
                german_title=translate(title)
                german_body=translate(body)
            except Exception as exc:
                print(f'Translation failed for {gid}; will retry next run: {exc}')
                continue
            url=item.get('url','https://store.steampowered.com/news/app/3393110')
            chunks=split_text(german_body)
            try:
                send(f'⚔️ **AION 2 – {german_title[:180]}**\n📜 Original: {url}\n\n'+(chunks[0] if chunks else ''))
                for chunk in chunks[1:]: send(chunk)
            except Exception as exc:
                print(f'Discord delivery failed for {gid}; will retry: {exc}')
                continue
            print(f'Posted {gid}: {title}')
        seen.add(gid)
    # Keep a rolling history, including non-patch news.
    STATE.write_text(json.dumps(sorted(seen)[-2000:],indent=2)+'\n')

if __name__=='__main__': main()
