# 🔑 ШАГ 1: ТОЛЬКО sys/os — НИКАКИХ РАННИХ ИМПОРТОВ
import os
import sys
os.environ['PYWEBVIEW_BACKEND'] = 'edgechromium'
# 🛡️ Блокируем случайную загрузку winforms/pythonnet
for mod in list(sys.modules.keys()):
    if mod.startswith('webview') or mod == 'clr':
        del sys.modules[mod]

# 🔑 ШАГ 2: Импортируем всё, кроме webview
import requests
import re
import json
import asyncio
import aiohttp
import random
import socket
import whois
import time
import threading
import concurrent.futures
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
import webbrowser
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import io as std_io
try:
    from fake_useragent import UserAgent
    def get_random_user_agent():
        return UserAgent().random
except ImportError:
    def get_random_user_agent():
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Доп. импорты для фото-поиска
import tempfile

# 🔑 ШАГ 3: ТОЛЬКО ЗДЕСЬ импортируем webview
import webview

# === LICENSING SYSTEM ===
HARD_CODED_KEYS = {
    "A1b2C3d4E5f6DAY": "day", "G7h8I9j0K1l2DAY": "day", "M3n4O5p6Q7r8DAY": "day",
    "S9t0U1v2W3x4DAY": "day", "Y5z6A7b8C9d0DAY": "day", "E1f2G3h4I5j6DAY": "day",
    "K7l8M9n0O1p2DAY": "day", "Q3r4S5t6U7v8DAY": "day", "W9x0Y1z2A3b4DAY": "day",
    "C5d6E7f8G9h0DAY": "day", "I1j2K3l4M5n6DAY": "day", "O7p8Q9r0S1t2DAY": "day",
    "U3v4W5x6Y7z8DAY": "day", "A9b0C1d2E3f4DAY": "day", "G5h6I7j8K9l0DAY": "day",
    "M1n2O3p4Q5r6DAY": "day", "S7t8U9v0W1x2DAY": "day", "Y3z4A5b6C7d8DAY": "day",
    "E9f0G1h2I3j4WEEK": "week", "K5l6M7n8O9p0WEEK": "week", "Q1r2S3t4U5v6WEEK": "week",
    "W7x8Y9z0A1b2WEEK": "week", "C3d4E5f6G7h8WEEK": "week", "I9j0K1l2M3n4WEEK": "week",
    "O5p6Q7r8S9t0WEEK": "week", "U1v2W3x4Y5z6WEEK": "week", "A7b8C9d0E1f2WEEK": "week",
    "G3h4I5j6K7l8WEEK": "week", "M9n0O1p2Q3r4WEEK": "week", "S5t6U7v8W9x0WEEK": "week",
    "Y1z2A3b4C5d6WEEK": "week", "E7f8G9h0I1j2WEEK": "week", "K3l4M5n6O7p8WEEK": "week",
    "Q9r0S1t2U3v4WEEK": "week", "W5x6Y7z8A9b0WEEK": "week",
    "Z1y2X3w4V5u6T7s8MONTH": "month", "B9a0C1d2E3f4G5h6MONTH": "month",
    "I8j7K6l5M4n3O2p1MONTH": "month", "Q0r9S8t7U6v5W4x3MONTH": "month",
    "Y2z1A0b9C8d7E6f5MONTH": "month", "G4h3I2j1K0l9M8n7MONTH": "month",
    "O6p5Q4r3S2t1U0v9MONTH": "month", "W8x7Y6z5A4b3C2d1MONTH": "month",
    "E0f9G8h7I6j5K4l3MONTH": "month", "M2n1O0p9Q8r7S6t5MONTH": "month",
    "C1d2E3f4G5h6FOREVER": "forever", "I7j8K9l0M1n2FOREVER": "forever",
    "O3p4Q5r6S7t8FOREVER": "forever", "U9v0W1x2Y3z4FOREVER": "forever",
    "A5b6C7d8E9f0FOREVER": "forever", "G1h2I3j4K5l6FOREVER": "forever",
    "M7n8O9p0Q1r2FOREVER": "forever", "S3t4U5v6W7x8FOREVER": "forever",
    "Y9z0A1b2C3d4FOREVER": "forever", "E5f6G7h8I9j0FOREVER": "forever",
    "K1l2M3n4O5p6FOREVER": "forever", "Q7r8S9t0U1v2FOREVER": "forever",
    "W3x4Y5z6A7b8FOREVER": "forever", "C9d0E1f2G3h4FOREVER": "forever",
    "I5j6K7l8M9n0FOREVER": "forever", "000": "forever"
}

def _calculate_expiry(duration: str):
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    if duration == "day": return now + timedelta(days=1)
    if duration == "week": return now + timedelta(weeks=1)
    if duration == "month": return now + timedelta(days=30)
    return None  # forever

def validate_license_key(key: str):
    key = key.strip()
    duration = HARD_CODED_KEYS.get(key)
    if not duration:
        return {"valid": False, "error": "Invalid key", "label": "", "expires_at": ""}
    expires_at = _calculate_expiry(duration)
    if expires_at:
        from datetime import datetime, timezone
        if datetime.now(timezone.utc) >= expires_at:
            return {"valid": False, "error": "Key expired", "label": duration.capitalize(), "expires_at": ""}
    return {
        "valid": True,
        "error": "",
        "label": duration.capitalize(),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S UTC") if expires_at else "Never"
    }

# ============= FunStat API CONFIG =============
FUNSTAT_API_KEY = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDMzMDI5NDc1IiwianRpIjoiMzA0Njg1ODQtZWE0MC00ZDk3LTkzNGQtZTJkYjYzNDlkOTNlIiwiZXhwIjoxNzk0MjI2NTgzfQ.as-QW6NXqgavP6o-S42qmz0qXR-jceOuU1IhXsa9QKsxvyPcIiEXldIQV2P743YoIdnqY3bQLp38Mf3qwJbtKYLw31AsaZA6L4KxVLFybKSqhxkyD8Xyis9057DX1kkeYxWHNLmcO4GbLgw9zO69gst2kh6_UG2I8pP4E0rUVBY'
FUNSTAT_API_BASE = "https://funstat.info/api/v1"
FUNSTAT_HEADERS = {
    "Authorization": f"Bearer {FUNSTAT_API_KEY}",
    "Content-Type": "application/json",
    "accept": "application/json"
}

def escape_html(text):
    if text is None: return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    return text

def format_short_date(date_str):
    try:
        if date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%d.%m.%Y')
        return "Нет данных"
    except:
        return date_str

def format_full_date(date_str):
    try:
        if date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%d.%m.%Y %H:%M:%S')
        return "Нет данных"
    except:
        return date_str

def get_media_type_name(media_code):
    media_types = {
        1: "ФОТО", 2: "ВИДЕО", 3: "АУДИО", 4: "ФАЙЛ", 5: "ГЕО",
        6: "КОНТАКТ", 7: "КРУЖОК", 8: "ГОЛОСОВОЕ", 9: "ВИДЕОСООБЩЕНИЕ",
        10: "СТИКЕР", 11: "АНИМАЦИЯ", 12: "ИГРА", 13: "ОПЛАТА",
        14: "ЗВОНОК", 15: "ОПРОС", 16: "ЛОКАЦИЯ"
    }
    return media_types.get(media_code, f"МЕДИА-{media_code}")

async def resolve_username(username):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/resolve_username",
            headers=FUNSTAT_HEADERS,
            params={"name": username}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data') and len(data['data']) > 0:
                return data['data'][0]['id']
        return None
    except Exception as e:
        return None

async def get_username_usage(username):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/username_usage",
            headers=FUNSTAT_HEADERS,
            params={"username": username}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', [])
        return []
    except Exception as e:
        return []

async def get_names_history(user_id):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/{user_id}/names",
            headers=FUNSTAT_HEADERS
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                return data['data']
        return []
    except Exception as e:
        return []

async def get_usernames_history(user_id):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/{user_id}/usernames",
            headers=FUNSTAT_HEADERS
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                return data['data']
        return []
    except Exception as e:
        return []

async def get_user_stats(user_id):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/{user_id}/stats",
            headers=FUNSTAT_HEADERS
        )
        if response.status_code == 200:
            stats_data = response.json()
            if stats_data.get('success') and stats_data.get('data'):
                return stats_data['data']
        return None
    except Exception as e:
        return None

async def get_user_messages(user_id, page=1, page_size=1000, media_filter=None):
    try:
        params = {"page": page, "pageSize": page_size}
        if media_filter and media_filter != 'all':
            params["media_code"] = int(media_filter)
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/{user_id}/messages",
            params=params,
            headers=FUNSTAT_HEADERS
        )
        if response.status_code == 200:
            messages_data = response.json()
            if messages_data.get('success') and messages_data.get('data'):
                return messages_data
        return None
    except Exception as e:
        return None

async def get_user_groups(user_id, page=1, page_size=1000):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/{user_id}/groups",
            headers=FUNSTAT_HEADERS,
            params={"page": page, "pageSize": page_size}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                return data
        return None
    except Exception as e:
        return None

async def get_user_reputation(user_id):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/users/reputation",
            headers=FUNSTAT_HEADERS,
            params={"id": user_id}
        )
        if response.status_code == 200:
            data = response.json()
            return data
        return None
    except Exception as e:
        return None

async def search_text_messages(search_text, page=1, page_size=1000):
    try:
        response = requests.get(
            f"{FUNSTAT_API_BASE}/text/search",
            params={"input": search_text, "page": page, "pageSize": page_size},
            headers=FUNSTAT_HEADERS
        )
        if response.status_code == 200:
            search_data = response.json()
            if search_data.get('success') and search_data.get('data'):
                return search_data['data']
        return None
    except Exception as e:
        return None

# 🔹 ФУНКЦИИ ДЛЯ ПОИСКА ПО ФОТО (НОВЫЕ)
def search_faces_api(image_path):
    url = "https://similarfaces.me/api/search-faces"
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            resp = requests.post(url, files=files, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"ok": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def parse_vk_profile_minimal(vk_id):
    try:
        url = f"https://vk.com/id{vk_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.find('title')
        name = title.text.split('|')[0].strip() if title else f"ID{vk_id}"
        city_elem = soup.find('div', class_='profile_info_row')
        city = city_elem.text.strip() if city_elem else ""
        return {"name": name, "city": city}
    except:
        return {"name": f"ID{vk_id}", "city": ""}

# ============= ОСНОВНЫЕ КЛАССЫ =============
class HttpWebNumber:
    def __init__(self):
        self.__check_number_link = "https://htmlweb.ru/geo/api.php?json&telcod="
        self.__not_found_text = "No information"
    def lookup(self, user_number: str) -> dict:
        try:
            response = requests.get(self.__check_number_link + user_number, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
            if response.ok:
                return response.json()
        except Exception:
            pass
        return {"status_error": True}

class Api:
    def __init__(self):
        self.print_lock = threading.Lock()

    def _random_ua(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # 🔹 НОВЫЙ: поиск по фото
    def search_faces(self, image_b64: str):
        try:
            # Decode & save temp image
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]
            img_data = base64.b64decode(image_b64)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name

            try:
                raw_res = search_faces_api(tmp_path)
                if not raw_res.get('ok', False) or not raw_res.get('results'):
                    return {"success": False, "error": raw_res.get("error", "No results"), "raw": raw_res}

                enriched = []
                for person in raw_res['results']:
                    vk_id = str(person.get('vk_id', ''))
                    extra = parse_vk_profile_minimal(vk_id) if vk_id.isdigit() else {}
                    person.update(extra)
                    # Добавим preview фото как base64 (маленький thumbnail)
                    img_url = person.get('image_url', '')
                    if img_url and img_url.startswith('http'):
                        try:
                            resp = requests.get(img_url, timeout=5)
                            if resp.status_code == 200:
                                thumb = Image.open(io.BytesIO(resp.content))
                                thumb.thumbnail((150, 150))
                                buf = io.BytesIO()
                                thumb.save(buf, format='JPEG')
                                person['image_b64'] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
                        except:
                            pass
                    enriched.append(person)

                return {
                    "success": True,
                    "results": enriched,
                    "raw": raw_res
                }
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            return {"success": False, "error": str(e), "raw": {}}

    # 🔹 FUNSTAT FULL INTEGRATION (все методы как в оригинале)
    def funstat_resolve_username(self, username):
        loop = asyncio.new_event_loop()
        try:
            res = loop.run_until_complete(resolve_username(username))
            return {"success": True, "user_id": res} if res else {"success": False, "error": "Not found"}
        finally:
            loop.close()

    def funstat_username_usage(self, username):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_username_usage(username))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    def funstat_user_stats(self, user_id):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_user_stats(user_id))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    def funstat_user_messages(self, user_id, media_filter='all'):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_user_messages(user_id, 1, media_filter))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    def funstat_user_groups(self, user_id):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_user_groups(user_id, 1))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    def funstat_user_reputation(self, user_id):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_user_reputation(user_id))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    def funstat_text_search(self, query):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_text_search_results(query, 1))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    def funstat_ai_analysis(self, user_id):
        loop = asyncio.new_event_loop()
        try:
            text, raw = loop.run_until_complete(show_ai_analysis(user_id))
            return {"success": True, "text": text, "raw": raw}
        finally:
            loop.close()

    # 🔹 BigBase
    def bigbase_search(self, query: str):
        try:
            headers = {"Authorization": "bntoBz7CQLoWXW2sgp0YXdGTL5qPve2x"}
            payload = {"search": query, "page": 0}
            r = requests.post("https://bigbase.top/api/search", headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            raw = r.json()
            if isinstance(raw, dict):
                raw.pop('token', None)
                raw.pop('api_key', None)
                raw.pop('Authorization', None)
                def clean_dict(d):
                    if isinstance(d, dict):
                        d.pop('token', None)
                        d.pop('api_key', None)
                        for v in d.values():
                            if isinstance(v, dict):
                                clean_dict(v)
                            elif isinstance(v, list):
                                for item in v:
                                    if isinstance(item, dict):
                                        clean_dict(item)
                clean_dict(raw)
            return {"success": True, "results": raw, "raw": raw}
        except Exception as e:
            return {"success": False, "error": str(e), "raw": {}}

    def funstat_search_username(self, username: str):
        try:
            headers = {
                "Authorization": f"Bearer {FUNSTAT_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {"search": username, "type": "username"}
            r = requests.post("https://funstat.info/api/v1/search", headers=headers, json=payload, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    data.pop('token', None)
                    data.pop('api_key', None)
                return {"success": True, "results": data, "raw": data}
            else:
                return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}", "raw": {}}
        except Exception as e:
            return {"success": False, "error": str(e), "raw": {}}

    def search_username(self, username: str):
        social_networks = [
            {'name': 'Instagram', 'url': f'https://instagram.com/{username}', 'checker': self._check_instagram_profile},
            {'name': 'Twitter/X', 'url': f'https://twitter.com/{username}', 'checker': self._check_twitter_profile},
            {'name': 'GitHub', 'url': f'https://github.com/{username}', 'checker': self._check_github_profile},
            {'name': 'VK', 'url': f'https://vk.com/{username}', 'checker': self._check_vk_profile},
            {'name': 'Facebook', 'url': f'https://facebook.com/{username}', 'checker': self._check_facebook_profile},
            {'name': 'Telegram', 'url': f'https://t.me/{username}', 'checker': self._check_telegram_profile},
            {'name': 'YouTube', 'url': f'https://youtube.com/@{username}', 'checker': self._check_youtube_profile},
            {'name': 'TikTok', 'url': f'https://tiktok.com/@{username}', 'checker': self._check_tiktok_profile},
            {'name': 'Reddit', 'url': f'https://reddit.com/user/{username}', 'checker': self._check_reddit_profile},
            {'name': 'LinkedIn', 'url': f'https://linkedin.com/in/{username}', 'checker': self._check_linkedin_profile},
            {'name': 'Pinterest', 'url': f'https://pinterest.com/{username}', 'checker': self._check_pinterest_profile},
            {'name': 'Twitch', 'url': f'https://twitch.tv/{username}', 'checker': self._check_twitch_profile},
        ]
        results = []
        headers = {'User-Agent': self._random_ua()}
        for net in social_networks:
            try:
                r = requests.get(net['url'], headers=headers, timeout=10, allow_redirects=True)
                results.append(net['checker'](r, net['url'], username))
            except Exception as e:
                results.append({'site': net['name'], 'url': net['url'], 'status': 'Error', 'error': str(e)})
        return {'success': True, 'username': username, 'results': results, "raw": {"username": username, "services": results}}

    def _check_instagram_profile(self, r, url, u):
        return {'site': 'Instagram', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_twitter_profile(self, r, url, u):
        return {'site': 'Twitter/X', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_github_profile(self, r, url, u):
        return {'site': 'GitHub', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_vk_profile(self, r, url, u):
        return {'site': 'VK', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_facebook_profile(self, r, url, u):
        return {'site': 'Facebook', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_telegram_profile(self, r, url, u):
        return {'site': 'Telegram', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_youtube_profile(self, r, url, u):
        return {'site': 'YouTube', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_tiktok_profile(self, r, url, u):
        return {'site': 'TikTok', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_reddit_profile(self, r, url, u):
        return {'site': 'Reddit', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_linkedin_profile(self, r, url, u):
        return {'site': 'LinkedIn', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_pinterest_profile(self, r, url, u):
        return {'site': 'Pinterest', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}
    def _check_twitch_profile(self, r, url, u):
        return {'site': 'Twitch', 'url': url, 'status': 'Found' if r.status_code == 200 else 'Not found'}

    def email_search(self, email: str):
        results = []
        try:
            url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={quote_plus(email)}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                stealers = r.json().get("stealers", [])
                for s in stealers[:3]:
                    results.append({
                        'source': 'HudsonRock',
                        'computer_name': s.get('computer_name', 'N/A'),
                        'operating_system': s.get('operating_system', 'N/A'),
                        'infection_date': s.get('date_compromised', 'N/A'),
                        'malware_path': s.get('malware_path', 'N/A'),
                        'ip': s.get('ip', 'N/A'),
                        'country_code': s.get('country_code', 'N/A')
                    })
        except: pass
        try:
            hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote_plus(email)}"
            hibp_resp = requests.get(hibp_url, headers={'User-Agent': 'OSINT-Tool-1.0'}, timeout=10)
            if hibp_resp.status_code == 200:
                breaches = hibp_resp.json()
                results.append({
                    'source': 'HaveIBeenPwned',
                    'breaches_count': len(breaches),
                    'breaches': [b.get('Name', 'Unknown') for b in breaches[:5]]
                })
        except: pass
        return {'success': bool(results), 'email': email, 'results': results, 'raw': {"email": email, "leaks": results}} if results else {'success': False, 'error': 'Email not found in leak DBs', 'raw': {}}

    def vk_osint(self, query: str):
        try:
            user_info = self._get_vk_user_info(query)
            if not user_info:
                return {'success': False, 'error': 'User not found', 'raw': {}}
            user_id = user_info.get('id', '')
            result = {
                'user_info': user_info,
                'posts': self._get_vk_user_posts(user_id),
                'friends': self._get_vk_friends(user_id),
                'groups': self._get_vk_groups(user_id),
            }
            formatted = self._format_vk_results(result)
            download_filename = f"vk_info_{query}.txt"
            with open(download_filename, 'w', encoding='utf-8') as f:
                f.write(formatted)
            return {'success': True, 'formatted': formatted, 'raw_data': result, 'raw': result}
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}

    def _get_vk_user_info(self, username: str):
        url = f"https://vk.com/{username}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            profile_info = {}
            profile_block = soup.find('div', {'id': 'profile_info'})
            if profile_block:
                name_element = profile_block.find('h1', class_='page_name')
                if name_element:
                    profile_info['name'] = name_element.get_text(strip=True)
                status_element = profile_block.find('div', class_='pp_status')
                if status_element:
                    profile_info['status'] = status_element.get_text(strip=True)
            info_rows = soup.find_all('div', class_='profile_info_row')
            for row in info_rows:
                label = row.find('div', class_='label').get_text(strip=True) if row.find('div', class_='label') else 'Unknown'
                value = row.find('div', class_='labeled').get_text(strip=True) if row.find('div', class_='labeled') else ''
                profile_info[label] = value
            followers_element = soup.find('a', {'href': f'/{username}/followers'})
            if followers_element:
                followers_text = followers_element.find('span', class_='count').get_text(strip=True)
                profile_info['followers'] = followers_text
            user_id_input = soup.find('input', {'name': 'to_id'})
            if user_id_input and 'value' in user_id_input.attrs:
                profile_info['id'] = user_id_input['value']
            return profile_info
        except Exception as e:
            return {'error': str(e)}

    def _get_vk_user_posts(self, user_id: str):
        if not user_id: return []
        url = f"https://vk.com/wall{user_id}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = []
            post_blocks = soup.find_all('div', class_='wall_text')
            for post_block in post_blocks[:5]:
                post = {}
                text_element = post_block.find('div', class_='wall_post_text')
                if text_element:
                    post['text'] = text_element.get_text(strip=True)
                date_element = post_block.find('span', class_=re.compile(r'rel_date'))
                if date_element:
                    post['date'] = date_element.get_text(strip=True)
                if post:
                    posts.append(post)
            return posts
        except:
            return []

    def _get_vk_friends(self, user_id: str):
        if not user_id: return []
        url = f"https://vk.com/friends?id={user_id}&section=all"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            friends = []
            friend_blocks = soup.find_all('div', class_=re.compile(r'friends_user_row'))
            for friend_block in friend_blocks[:10]:
                friend = {}
                name_element = friend_block.find('a', class_=re.compile(r'friends_field_title'))
                if name_element:
                    friend['name'] = name_element.get_text(strip=True)
                    if 'href' in name_element.attrs:
                        friend['link'] = f"https://vk.com{name_element['href']}"
                city_element = friend_block.find('div', class_=re.compile(r'friends_field'))
                if city_element:
                    friend['city'] = city_element.get_text(strip=True)
                if friend:
                    friends.append(friend)
            return friends
        except:
            return []

    def _get_vk_groups(self, user_id: str):
        if not user_id: return []
        url = f"https://vk.com/groups?act=groups&id={user_id}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            groups = []
            group_blocks = soup.find_all('div', class_=re.compile(r'group_row|groups_row'))
            for group_block in group_blocks[:5]:
                group = {}
                name_element = group_block.find('a', class_=re.compile(r'group_title|groups_row_title'))
                if name_element:
                    group['name'] = name_element.get_text(strip=True)
                    if 'href' in name_element.attrs:
                        group['link'] = f"https://vk.com{name_element['href']}"
                members_element = group_block.find('div', class_=re.compile(r'group_info|groups_row_members'))
                if members_element:
                    group['members'] = members_element.get_text(strip=True)
                if group:
                    groups.append(group)
            return groups
        except:
            return []

    def _format_vk_results(self, data: dict) -> str:
        output = []
        if user_info := data.get('user_info'):
            output.append("🔍 Основная информация о профиле")
            if name := user_info.get('name'):
                output.append(f"Имя: {name}")
            if status := user_info.get('status'):
                output.append(f"Статус: {status}")
            if followers := user_info.get('followers'):
                output.append(f"Подписчики: {followers}")
            for key, value in user_info.items():
                if key not in ['name', 'status', 'followers', 'id']:
                    output.append(f"{key}: {value}")
            output.append("")
        if posts := data.get('posts'):
            output.append("📰 Последние посты пользователя")
            for i, post in enumerate(posts, 1):
                text = post.get('text', 'Текст отсутствует')
                date = post.get('date', 'Дата неизвестна')
                output.append(f"{i}. ({date}) {text}")
            output.append("")
        if friends := data.get('friends'):
            output.append("👥 Список друзей")
            for friend in friends:
                name = friend.get('name', 'Неизвестный')
                city = friend.get('city', 'Город неизвестен')
                link = friend.get('link', 'Ссылка отсутствует')
                output.append(f"- {name} ({city}) - {link}")
            output.append("")
        if groups := data.get('groups'):
            output.append("📚 Группы пользователя")
            for group in groups:
                name = group.get('name', 'Неизвестная группа')
                members = group.get('members', 'Участников неизвестно')
                link = group.get('link', 'Ссылка отсутствует')
                output.append(f"- {name} (👥 {members}) - {link}")
        return "\n".join(output)

    def lookup_ip(self, ip: str):
        if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
            return {'success': False, 'error': 'Invalid IP', 'raw': {}}
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get('status') == 'success':
                    return {'success': True, **d, 'raw': d}
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}
        return {'success': False, 'error': 'No data', 'raw': {}}

    def lookup_hlr(self, number: str):
        url = "https://www.ipqualityscore.com/api/json/phone"
        params = {'key': 'Test', 'phone': number}
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if not data.get('success'):
                return {'success': False, 'error': data.get('message', 'HLR lookup failed'), 'raw': {}}
            return {'success': True, **data, 'raw': data}
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}

    def search_reveng(self, query: str):
        enc = quote_plus(query)
        headers = {'User-Agent': self._random_ua()}
        url = f'https://reveng.ee/search?q={enc}&per_page=100'
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []
            links = set(a['href'] for a in soup.find_all('a', href=True) if 'entity' in a['href'])
            for link in list(links)[:5]:
                full = link if link.startswith('http') else f'https://reveng.ee{link}'
                sub = requests.get(full, headers=headers, timeout=10)
                sub_soup = BeautifulSoup(sub.text, 'html.parser')
                info = sub_soup.find('div', class_='bg-body rounded shadow-sm p-3 mb-2 entity-info')
                if not info: continue
                entry = {}
                name_span = info.find('span', class_='entity-prop-value')
                if name_span:
                    entry['Name'] = name_span.get_text(strip=True)
                for row in info.find_all('tr', class_='property-row'):
                    k = row.find('td', class_='property-name')
                    v = row.find('td', class_='property-values')
                    if k and v:
                        entry[k.get_text(strip=True)] = v.get_text(strip=True)
                if entry:
                    results.append(entry)
            return {'success': True, 'results': results, 'raw': {"query": query, "results": results}}
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}

    def generate_dorks(self, query: str):
        query = query.strip()
        t = 'general'
        if re.match(r'^(\+7|8)[\d\-\(\)\s]{10,}$', query): t = 'phone'
        elif re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', query): t = 'ip'
        elif re.match(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?$', query): t = 'name'
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query): t = 'email'
        dorks_map = {
            'phone': [f'"{query}" site:facebook.com', f'"{query}" site:linkedin.com', f'"{query}" site:vk.com',
                      f'"{query}" site:ok.ru', f'"{query}" site:truecaller.com', f'"{query}" "телефон" OR "phone"',
                      f'"{query}" "контакты" OR "contacts"'],
            'email': [f'"{query}" site:facebook.com', f'"{query}" site:linkedin.com', f'"{query}" site:twitter.com',
                      f'"{query}" filetype:pdf', f'"{query}" "contact" OR "email"', f'"{query}" "резюме" OR "cv"'],
            'name': [f'"{query}" site:facebook.com', f'"{query}" site:linkedin.com', f'"{query}" site:vk.com',
                     f'"{query}" site:instagram.com', f'"{query}" "работает" OR "works"', f'"{query}" filetype:pdf "резюме"'],
            'ip': [f'"{query}" "whois"', f'"{query}" "geolocation"', f'"{query}" "ISP"',
                   f'"{query}" "malware" OR "virus"', f'"{query}" "abuse" OR "spam"'],
            'general': [f'"{query}" site:facebook.com', f'"{query}" site:linkedin.com', f'"{query}" site:twitter.com',
                        f'"{query}" filetype:pdf', f'"{query}" "contacts" OR "контакты"']
        }
        res = {'success': True, 'query_type': t, 'query': query, 'dorks': dorks_map.get(t, [])}
        return {**res, 'raw': res}

    def database_search(self, keyword: str):
        db_dir = 'data'
        if not os.path.exists(db_dir):
            return {'success': False, 'error': f"Folder '{db_dir}' does not exist", 'raw': {}}
        files = [os.path.join(root, f) for root, _, files_ in os.walk(db_dir) for f in files_]
        results_list = []
        stop = threading.Event()
        with concurrent.futures.ThreadPoolExecutor() as exe:
            fut = [exe.submit(self._search_file, fp, keyword, stop, results_list) for fp in files if not stop.is_set()]
            concurrent.futures.wait(fut)
        out = [f"File: {fp} | Line {ln}: {match}" for fp, ln, match in results_list]
        return {'success': True, 'keyword': keyword, 'matches_found': len(out), 'results': out, 'raw': {"keyword": keyword, "matches": results_list}}

    def _search_file(self, fp, kw, stop, results_list):
        try:
            with open(fp, encoding='utf-8', errors='ignore') as f:
                for ln, line in enumerate(f, 1):
                    if stop.is_set(): return
                    if kw.lower() in line.lower():
                        results_list.append((fp, ln, line.strip()))
        except: pass

    def phone_lookup(self, number: str):
        results = {}
        try:
            nv = requests.get(f"http://apilayer.net/api/validate?access_key={getattr(self, 'PHONE_API_KEY', 'NONE')}&number={number}", timeout=7).json()
            if nv.get('valid'):
                results['numverify'] = nv
        except: pass
        try:
            ab = requests.get(f"https://phonevalidation.abstractapi.com/v1/?api_key={getattr(self, 'ABSTRACT_API_KEY', 'NONE')}&phone={number}", timeout=5).json()
            if ab.get('valid'):
                results['abstract'] = ab
        except: pass
        try:
            hw = HttpWebNumber().lookup(number)
            if not hw.get('status_error'):
                results['htmlweb'] = hw
        except: pass
        return {'success': bool(results), 'number': number, 'results': results, 'raw': {"number": number, "sources": results}}

    def enhanced_ip_lookup(self, ip: str):
        results = {}
        try:
            ipapi = requests.get(f"http://ip-api.com/json/{ip}", timeout=7).json()
            if ipapi.get('status') == 'success':
                results['ipapi'] = ipapi
        except: pass
        try:
            ipinfo = requests.get(f"https://ipinfo.io/{ip}/json?token={getattr(self, 'IPINFO_API_KEY', 'NONE')}", timeout=5).json()
            results['ipinfo'] = ipinfo
        except: pass
        try:
            shodan = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={getattr(self, 'SHODAN_API_KEY', 'NONE')}", timeout=10).json()
            results['shodan'] = shodan
        except: pass
        return {'success': bool(results), 'ip': ip, 'results': results, 'raw': {"ip": ip, "sources": results}}

    def domain_whois(self, domain: str):
        try:
            domain = (urlparse(domain).netloc or domain).split('/')[0]
            w = whois.whois(domain)
            res = {
                'domain': domain,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': list(w.name_servers) if w.name_servers else [],
                'emails': w.emails if w.emails else []
            }
            if domain.endswith('.ru') or domain.endswith('.рф'):
                try:
                    ru = requests.get(f"https://www.nic.ru/whois/?query={domain}", timeout=5).text
                    res['nic_ru'] = ru
                except: pass
            full_res = {'success': True, 'results': res, 'raw': res}
            return full_res
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}

    def leak_search(self, token: str, query: str):
        try:
            r = requests.post('https://leakosintapi.com/', json={'token': token, 'request': query, 'limit': 1000000}, timeout=15)
            r.raise_for_status()
            data = r.json()
            return {'success': True, 'results': data, 'raw': data}
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}

    def mac_vendor_lookup(self, mac: str):
        mac = mac.lower().replace('-', ':').replace('.', ':')
        try:
            r = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
            if r.status_code == 200:
                return {'success': True, 'mac': mac, 'vendor': r.text, 'raw': {"mac": mac, "vendor": r.text}}
        except: pass
        try:
            r = requests.get(f"https://macvendors.co/api/{mac}", timeout=5).json()
            if 'result' in r:
                return {'success': True, 'mac': mac, 'vendor': r['result'].get('company', 'Unknown'), 'raw': {"mac": mac, "vendor": r['result']}}
        except: pass
        return {'success': False, 'error': 'Vendor not found', 'raw': {}}

    def depsearch_lookup(self, query: str):
        url = f'https://api.depsearch.digital/quest={query}?token={getattr(self, "DEPSEARCH_TOKEN", "NONE")}&lang=ru'
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            if not data.get('results'):
                return {'success': False, 'error': 'No results', 'raw': {}}
            return {'success': True, 'results': data['results'], 'raw': data}
        except Exception as e:
            return {'success': False, 'error': str(e), 'raw': {}}

    def generate_qr_code(self, text: str):
        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="white", back_color="#0a1a35")
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return {'success': True, 'qr_code': f"data:image/png;base64,{img_str}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_identity_card(self, name: str, age: str, address: str, phone: str, email: str):
        try:
            img = Image.new('RGB', (400, 250), color='#0a1a35')
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            d.rectangle([(10, 10), (390, 240)], outline='white', width=2)
            d.text((20, 20), "IDENTITY CARD", font=font, fill='white')
            d.text((20, 50), f"Name: {name}", font=font, fill='white')
            d.text((20, 80), f"Age: {age}", font=font, fill='white')
            d.text((20, 110), f"Address: {address}", font=font, fill='white')
            d.text((20, 140), f"Phone: {phone}", font=font, fill='white')
            d.text((20, 170), f"Email: {email}", font=font, fill='white')
            date_str = time.strftime("%Y-%m-%d")
            d.text((20, 200), f"Issued: {date_str}", font=font, fill='white')
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return {'success': True, 'id_card': f"data:image/png;base64,{img_str}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Асинхронные вспомогательные функции FunStat (скопированы из файла)
async def show_username_usage(username):
    try:
        text = ""
        usage_data = await get_username_usage(username)
        if not usage_data:
            return f"[ERROR] История использования username '@{username}' не найдена", {"names": []}
        for i, usage in enumerate(usage_data, 1):
            user_id = usage.get('user_id', 'Неизвестно')
            first_name = escape_html(usage.get('first_name', ''))
            last_name = escape_html(usage.get('last_name', ''))
            date_from = format_full_date(usage.get('date_from', ''))
            date_to = format_full_date(usage.get('date_to', ''))
            text += f"{i}. {first_name} {last_name}\n"
            text += f"   ID: {user_id}\n"
            text += f"   Использовался: {date_from}"
            if date_to != "Нет данных":
                text += f" - {date_to}"
            text += "\n"
        text += f"Всего пользователей с этим username: {len(usage_data)}"
        return text, {"username": username, "usage_history": usage_data}
    except Exception as e:
        return f"[ERROR] Ошибка при получении истории username: {str(e)}", {}

async def show_user_stats(user_id):
    try:
        text = ""
        stats_data = await get_user_stats(user_id)
        if not stats_data:
            return f"[ERROR] Статистика не найдена или API вернул ошибку", {}
        text = f"ДЕТАЛЬНАЯ СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ {user_id}\n"
        text += "=" * 50 + "\n"
        text += "ОСНОВНАЯ ИНФОРМАЦИЯ:\n"
        text += "-" * 20 + "\n"
        text += f"Имя: {escape_html(stats_data.get('first_name', 'Не указано'))}\n"
        if stats_data.get('last_name'):
            text += f"Фамилия: {escape_html(stats_data['last_name'])}\n"
        text += f"Бот: {'Да' if stats_data.get('is_bot') else 'Нет'}\n"
        text += f"Активен: {'Да' if stats_data.get('is_active') else 'Нет'}\n"
        text += "АКТИВНОСТЬ:\n"
        text += "-" * 20 + "\n"
        text += f"Первое сообщение: {format_short_date(stats_data.get('first_msg_date'))}\n"
        text += f"Последнее сообщение: {format_short_date(stats_data.get('last_msg_date'))}\n"
        text += "СТАТИСТИКА СООБЩЕНИЙ:\n"
        text += "-" * 20 + "\n"
        text += f"Всего сообщений: {stats_data.get('total_msg_count', 0):,}\n"
        text += f"Сообщений в группах: {stats_data.get('msg_in_groups_count', 0):,}\n"
        text += f"Админ в группах: {stats_data.get('adm_in_groups', 0)}\n"
        text += f"Всего групп: {stats_data.get('total_groups', 0)}\n"
        names_history = await get_names_history(user_id)
        usernames_history = await get_usernames_history(user_id)
        if names_history:
            text += f"ИСТОРИЯ ИМЕН ({len(names_history)}):\n"
            text += "-" * 20 + "\n"
            for i, name_record in enumerate(names_history[:9999], 1):
                date_str = format_short_date(name_record.get('date_time', ''))
                name = escape_html(name_record.get('name', 'Не указано'))
                text += f"{i}. {date_str} → {name}\n"
            if len(names_history) > 10:
                text += f"... и еще {len(names_history) - 10} записей\n"
            text += "\n"
        if usernames_history:
            text += f"ИСТОРИЯ USERNAME ({len(usernames_history)}):\n"
            text += "-" * 20 + "\n"
            for i, username_record in enumerate(usernames_history[:9999], 1):
                date_str = format_short_date(username_record.get('date_time', ''))
                username = escape_html(username_record.get('name', ''))
                if username:
                    text += f"{i}. {date_str} → @{username}\n"
                else:
                    text += f"{i}. {date_str} → Не указано\n"
            if len(usernames_history) > 10:
                text += f"... и еще {len(usernames_history) - 10} записей\n"
        raw_for_diagram = {
            "user_id": user_id,
            "names_history": names_history,
            "usernames_history": usernames_history,
            "stats": stats_data,
            "groups": [],
            "emails": [],
            "phones": []
        }
        return text, raw_for_diagram
    except Exception as e:
        return f"[ERROR] Ошибка при получении статистики: {str(e)}", {}

async def show_user_messages(user_id, page=1, media_filter=None):
    try:
        text = ""
        messages_data = await get_user_messages(user_id, page, 1000, media_filter)
        if not messages_data or not messages_data.get('data'):
            return f"[ERROR] Сообщения не найдены или API вернул ошибку", {}
        messages = messages_data.get('data', [])
        filter_text = f" ({get_media_type_name(int(media_filter))})" if media_filter and media_filter != 'all' else ""
        text += "[R] - ответ кому-то\n"
        for msg in messages:
            date_str = format_short_date(msg.get('date'))
            chat_title = escape_html(msg['group'].get('title', 'Unknown'))
            if msg.get('replyToMessageId'):
                reply_mark = "[R] "
            else:
                reply_mark = ""
            media_code = msg.get('mediaCode')
            media_name = msg.get('mediaName')
            if media_code:
                content_type = get_media_type_name(media_code)
                if media_name:
                    content_type += f" ({media_name})"
            else:
                msg_text = escape_html(msg.get('text', ''))
                if msg_text and len(msg_text) > 100:
                    msg_text = msg_text[:100] + "..."
                content_type = msg_text or "[ТЕКСТ]"
            text += f"{chat_title} [{date_str}] > {reply_mark}{content_type}\n"
        paging = messages_data.get('paging', {})
        total = paging.get('total', 0)
        current_page = paging.get('currentPage', 1)
        total_pages = paging.get('totalPages', 1)
        text += f"\nВсего {total:,}, страница {current_page} из {total_pages}"
        raw_for_diagram = {
            "user_id": user_id,
            "messages": messages,
            "media_filter": media_filter
        }
        return text, raw_for_diagram
    except Exception as e:
        return f"[ERROR] Ошибка при получении сообщений: {str(e)}", {}

async def show_user_groups(user_id, page=1):
    try:
        text = ""
        groups_data = await get_user_groups(user_id, page, 1000)
        if not groups_data or not groups_data.get('success') or not groups_data.get('data'):
            return f"[ERROR] Информация о группах не найдена", {}
        all_groups = groups_data['data']
        start_index = (page - 1) * 1000
        end_index = page * 1000
        groups = all_groups[start_index:end_index]
        paging = groups_data.get('paging', {})
        total = paging.get('total', len(all_groups))
        current_page = paging.get('currentPage', page)
        total_pages = paging.get('totalPages', max(1, (total + 1000 - 1) // 1000))
        for i, group in enumerate(groups, start=start_index + 1):
            chat_info = group.get('chat', {})
            group_title = escape_html(chat_info.get('title', 'Unknown'))
            messages_count = group.get('messagesCount', 0)
            last_message = format_short_date(group.get('last_message'))
            activity_indicator = "🔥" if messages_count > 50 else "💬" if messages_count > 10 else "👻"
            text += f"{i}. {group_title}\n"
            text += f"   {activity_indicator} Сообщений: {messages_count:,} | Последнее: {last_message}\n"
        text += f"Страница {current_page} из {total_pages} | Всего групп: {total:,}"
        raw_for_diagram = {
            "user_id": user_id,
            "groups": groups
        }
        return text, raw_for_diagram
    except Exception as e:
        return f"[ERROR] Ошибка при загрузке групп: {str(e)}", {}

async def show_user_reputation(user_id):
    try:
        text = ""
        stats_data = await get_user_stats(user_id)
        user_info = stats_data if stats_data else {}
        reputation_data = await get_user_reputation(user_id)
        username = f"@{user_info.get('username')}" if user_info.get('username') else ""
        text += f"{user_info.get('first_name', '')} {user_info.get('last_name', '')} ({username} | {user_id})\n"
        if reputation_data:
            text += f"Репутация: {reputation_data.get('reputation_name', 'Нет данных')}\n"
            text += f"Всего оценок: {reputation_data.get('num_votes', 0):,}\n"
            text += f"Положительных: {reputation_data.get('positive_count', 0):,}\n"
            text += f"Отрицательных: {reputation_data.get('negative_count', 0):,}\n"
            text += f"Средний балл: {reputation_data.get('simple_average', 0):.3f}\n"
            text += f"Отзывов: {reputation_data.get('review_count', 0):,}\n"
            text += f"Первая оценка: {format_short_date(reputation_data.get('first_time'))}\n"
            text += f"Последняя оценка: {format_short_date(reputation_data.get('last_time'))}\n"
        else:
            text += "Информация о репутации недоступна\n"
            text += "Пользователь еще не имеет оценок или произошла ошибка при получении данных"
        raw_for_diagram = {
            "user_id": user_id,
            "reputation": reputation_data,
        }
        return text, raw_for_diagram
    except Exception as e:
        return f"[ERROR] Ошибка при загрузке репутации: {str(e)}", {}

async def show_text_search_results(search_text, page=1):
    try:
        text = ""
        search_data = await search_text_messages(search_text, page, 1000)
        if not search_data or not search_data.get('data'):
            return f"[ERROR] Сообщения с текстом '{search_text}' не найдены", {}
        messages = search_data.get('data', [])
        for msg in messages:
            date_str = format_short_date(msg.get('date'))
            user_name = escape_html(msg.get('name', 'Unknown'))
            username = f"@{msg.get('username')}" if msg.get('username') else ""
            user_id = msg.get('user_id')
            msg_text = escape_html(msg.get('text', ''))
            chat_title = escape_html(msg['group'].get('title', 'Unknown'))
            text += f"{user_name} {username} ({user_id})\n"
            text += f"{chat_title} [{date_str}]\n"
            if len(msg_text) > 150:
                msg_text = msg_text[:150] + "..."
            text += f"{msg_text}\n"
        total = search_data.get('total', len(messages))
        current_page = search_data.get('currentPage', page)
        total_pages = search_data.get('totalPages', 1)
        text += f"Найдено сообщений: {total:,}, страница {current_page} из {total_pages}"
        raw_for_diagram = {
            "query": search_text,
            "messages": messages
        }
        return text, raw_for_diagram
    except Exception as e:
        return f"[ERROR] Ошибка при поиске текста: {str(e)}", {}

class AIAccountAnalyzer:
    def __init__(self):
        self.interests_categories = {
            'технологии': ['программирование', 'python', 'java', 'javascript', 'github', 'it', 'кибербезопасность', 'код', 'разработка', 'компьютер', 'софт', 'hardware', 'linux', 'windows', 'android', 'ios', 'html', 'css', 'php', 'sql'],
            'кибербезопасность': ['хакер', 'hacker', 'взлом', 'взломать', 'безопасность', 'security', 'пентест', 'pentest', 'кибер', 'cyber', 'уязвимость', 'exploit', 'backdoor'],
            'osint': ['osint', 'разведка', 'расследование', 'investigation', 'поиск', 'search', 'данные', 'data', 'информация', 'information'],
            'doxxing': ['dox', 'doxxing', 'doxing', 'докс', 'токен', 'доксинг', 'личные данные', 'personal data', 'приват', 'private', 'утечка', 'leak', 'база', 'base', 'bases', 'database'],
            'крипта': ['биткоин', 'bitcoin', 'эфириум', 'ethereum', 'блокчейн', 'blockchain', 'крипта', 'crypto', 'майнинг', 'mining', 'трейдинг', 'trading', 'nft', 'coin', 'wallet', 'кошелек'],
            'спорт': ['футбол', 'хоккей', 'баскетбол', 'теннис', 'спорт', 'тренировка', 'зал', 'качалка', 'бег', 'плавание', 'матч', 'чемпионат', 'бокс', 'мма', 'ufc', 'тренируюсь', 'качаюсь'],
            'авто': ['машина', 'авто', 'bmw', 'мерседес', 'audi', 'volkswagen', 'двигатель', 'тюнинг', 'водитель', 'драйв', 'тачка', 'запчасти', 'шины', 'масло', 'покрышки', 'диски'],
            'путешествия': ['путешествие', 'отпуск', 'отдых', 'отель', 'пляж', 'горы', 'море', 'авиабилет', 'гостиница', ' тур', 'курорт', 'виза', 'паспорт', 'чемодан', 'аэропорт'],
            'игры': ['игра', 'гейминг', 'steam', 'playstation', 'xbox', 'дота', 'dota', 'контрстрайк', 'cs', 'майнкрафт', 'minecraft', 'танки', 'wot', 'гта', 'gta', 'ранг', 'рейтинг'],
            'музыка': ['музыка', 'трек', 'альбом', 'концерт', 'исполнитель', 'плейлист', 'spotify', 'гитара', 'рок', 'поп', 'хип-хоп', 'рэп', 'диджей', 'бит', 'beat', 'микрофон'],
            'кино': ['фильм', 'кино', 'сериал', 'netflix', 'режиссер', 'актер', 'премьера', 'сцена', 'трейлер', 'оскар', 'мелодрама', 'комедия', 'ужасы', 'фантастика'],
            'бизнес': ['бизнес', 'стартап', 'инвестиции', 'компания', 'предприниматель', 'доход', 'прибыль', 'маркетинг', 'продажи', 'клиент', 'заработок', 'деньги'],
            'политика': ['политика', 'президент', 'правительство', 'выборы', 'партия', 'закон', 'государство', 'санкции', 'экономика', 'власть', 'оппозиция'],
            'образование': ['учеба', 'университет', 'студент', 'курс', 'обучение', 'образование', 'школа', 'преподаватель', 'экзамен', 'зачет', 'сессия', 'диплом'],
            'здоровье': ['здоровье', 'медицина', 'врач', 'болезнь', 'лечение', 'диета', 'фитнес', 'йога', 'спортзал', 'питание', 'витамины', 'больница'],
            'еда': ['еда', 'ресторан', 'кухня', 'рецепт', ' готовка', 'бургер', 'пицца', 'суши', 'кофе', 'чай', 'алкоголь', 'вино', 'пиво', 'водка'],
            'мода': ['мода', 'одежда', 'бренд', 'стиль', 'кроссовки', 'одежда', 'шопинг', 'магазин', 'скидка', 'распродажа', 'люкс', 'брендовый'],
            'хобби': ['хобби', 'коллекция', 'рукоделие', 'рисование', 'фотография', 'рыбалка', 'охота', 'садоводство', 'вязание', 'вышивка']
        }
        self.personality_traits = {
            'экстраверт': ['общение', 'друзья', 'вечеринка', 'встреча', 'компания', 'знакомство', 'тусовка', 'общаюсь', 'коммуникация'],
            'интроверт': ['дом', 'одиночество', 'тишина', 'книга', 'уединение', 'спокойствие', 'устал', 'усталость', 'отдых', 'один'],
            'творческий': ['искусство', 'творчество', 'рисование', 'музыка', 'писатель', 'креатив', 'вдохновение', 'идея', 'проект'],
            'аналитик': ['анализ', 'логика', 'данные', 'исследование', 'статистика', 'наука', 'техника', 'анализирую', 'исследую'],
            'лидер': ['руководство', 'лидер', 'организация', 'управление', 'команда', 'проект', 'ответственность', 'руковожу', 'управляю'],
            'консерватор': ['традиции', 'стабильность', 'надежность', 'порядок', 'дисциплина', 'правила', 'система', 'структура'],
            'новатор': ['инновации', 'новое', 'эксперимент', 'изменения', 'прогресс', ' будущее', 'инновационный', 'экспериментирую'],
            'оптимист': ['хорошо', 'отлично', 'прекрасно', 'рад', 'счастье', 'успех', 'победа', 'верю', 'надеюсь', 'позитив'],
            'пессимист': ['плохо', 'ужасно', 'проблема', 'жалоба', 'неудача', 'проигрыш', 'сложно', 'трудно', 'безнадежно'],
            'агрессивный': ['злой', 'злость', 'агрессия', 'раздражение', 'гнев', 'бесит', 'раздражает', 'ненависть', 'ненавижу'],
            'дружелюбный': ['друг', 'дружба', 'помощь', 'поддержка', 'добрый', 'хороший', 'приятный', 'помогаю', 'поддерживаю']
        }
        self.osint_keywords = [
            'osint', 'разведка', 'расследование', 'поиск информации', 'сбор данных', 
            'интернет-разведка', 'digital investigation', 'киберразведка',
            'dox', 'doxxing', 'doxing', 'докс', 'доксинг', 'личные данные',
            'приватная информация', 'утечка данных', 'база данных', 'database',
            'personal information', 'private data', 'leak', 'утечка',
            'reconnaissance', 'intelligence', 'information gathering'
        ]
    def analyze_interests(self, messages):
        all_text = ' '.join([msg.get('text', '') for msg in messages if msg.get('text')])
        all_text = all_text.lower()
        interests_scores = {}
        for category, keywords in self.interests_categories.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                found_keywords = [kw for kw in keywords if kw in all_text]
                intensity = 'очень высокая' if score > 20 else 'высокая' if score > 10 else 'средняя' if score > 5 else 'низкая'
                interests_scores[category] = {
                    'score': score,
                    'keywords': found_keywords,
                    'intensity': intensity,
                    'percentage': round((score / len(keywords)) * 100, 1)
                }
        return dict(sorted(interests_scores.items(), key=lambda x: x[1]['score'], reverse=True))
    def analyze_personality(self, messages):
        all_text = ' '.join([msg.get('text', '') for msg in messages if msg.get('text')])
        all_text = all_text.lower()
        trait_scores = {}
        for trait, keywords in self.personality_traits.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            trait_scores[trait] = {
                'score': score,
                'intensity': 'сильная' if score > 8 else 'умеренная' if score > 4 else 'слабая'
            }
        dominant_traits = sorted(trait_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:9999]
        return {
            'dominant_traits': dominant_traits,
            'personality_type': self._determine_personality_type(dominant_traits),
            'all_traits': trait_scores,
            'emotional_tone': self._analyze_emotional_tone(all_text)
        }
    def _analyze_emotional_tone(self, text):
        positive_words = ['хорошо', 'отлично', 'прекрасно', 'рад', 'счастье', 'успех', 'любовь', 'нравится']
        negative_words = ['плохо', 'ужасно', 'проблема', 'жалоба', 'неудача', 'ненависть', 'злость']
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        if pos_count > neg_count * 2:
            return "позитивный"
        elif neg_count > pos_count * 2:
            return "негативный"
        else:
            return "нейтральный"
    def _determine_personality_type(self, dominant_traits):
        if not dominant_traits:
            return "Не определен"
        primary_trait = dominant_traits[0][0]
        return primary_trait.capitalize()
    def analyze_social_connections(self, messages, user_id):
        user_mentions = {}
        for msg in messages:
            text = msg.get('text', '')
            if text:
                mentions = re.findall(r'@(\w+)', text)
                for mention in mentions:
                    user_mentions[mention] = user_mentions.get(mention, 0) + 1
        top_mentions = sorted(user_mentions.items(), key=lambda x: x[1], reverse=True)[:9999]
        return {
            'top_mentioned_users': top_mentions,
            'total_unique_mentions': len(user_mentions),
            'most_active_chats': self._analyze_chat_activity(messages)
        }
    def _analyze_chat_activity(self, messages):
        chat_activity = {}
        for msg in messages:
            chat_id = msg.get('group', {}).get('id')
            chat_title = msg.get('group', {}).get('title', 'Unknown')
            if chat_id:
                key = f"{chat_title} ({chat_id})"
                chat_activity[key] = chat_activity.get(key, 0) + 1
        return sorted(chat_activity.items(), key=lambda x: x[1], reverse=True)[:9999]
    def analyze_osint_doxxing_interest(self, messages):
        all_text = ' '.join([msg.get('text', '') for msg in messages if msg.get('text')])
        all_text = all_text.lower()
        osint_score = 0
        found_keywords = []
        for keyword in self.osint_keywords:
            if keyword in all_text:
                osint_score += 1
                found_keywords.append(keyword)
        risk_level = "высокий" if osint_score > 5 else "средний" if osint_score > 2 else "низкий"
        return {
            'osint_score': osint_score,
            'found_keywords': found_keywords,
            'risk_level': risk_level,
            'interest_level': 'активный интерес' if osint_score > 3 else 'умеренный интерес' if osint_score > 1 else 'минимальный интерес'
        }
    def analyze_personal_data_leaks(self, messages):
        leaks_found = {
            'phones': [],
            'emails': [],
            'cards': [],
            'addresses': []
        }
        phone_pattern = r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        card_pattern = r'\b\d{16}\b'
        address_patterns = [r'ул\.\s*\w+', r'улица\s*\w+', r'дом\s*\d+', r'кв\.\s*\d+']
        for msg in messages:
            text = msg.get('text', '')
            if text:
                phones = re.findall(phone_pattern, text)
                leaks_found['phones'].extend(phones)
                emails = re.findall(email_pattern, text)
                leaks_found['emails'].extend(emails)
                cards = re.findall(card_pattern, text)
                leaks_found['cards'].extend(cards)
                for pattern in address_patterns:
                    addresses = re.findall(pattern, text)
                    leaks_found['addresses'].extend(addresses)
        for key in leaks_found:
            leaks_found[key] = list(set(leaks_found[key]))
        return leaks_found
    def analyze_social_behavior(self, groups_data, messages):
        groups = groups_data.get('data', [])
        active_groups = [g for g in groups if g.get('messagesCount', 0) > 0]
        group_categories = self._categorize_groups(groups)
        time_analysis = self._analyze_time_patterns(messages)
        return {
            'total_groups': len(groups),
            'active_groups': len(active_groups),
            'group_categories': group_categories,
            'time_patterns': time_analysis,
            'social_level': 'очень активный' if len(active_groups) > 20 else 'активный' if len(active_groups) > 10 else 'умеренный' if len(active_groups) > 3 else 'пассивный'
        }
    def _categorize_groups(self, groups):
        categories = defaultdict(list)
        for group in groups:
            title = group.get('chat', {}).get('title', '').lower()
            messages_count = group.get('messagesCount', 0)
            group_info = {
                'title': group.get('chat', {}).get('title', 'Unknown'),
                'messages_count': messages_count
            }
            if any(word in title for word in ['it', 'tech', 'программирование', 'разработка', 'код', 'osint', 'hack']):
                categories['технологии'].append(group_info)
            elif any(word in title for word in ['крипта', 'биткоин', 'блокчейн', 'crypto']):
                categories['крипта'].append(group_info)
            elif any(word in title for word in ['osint', 'разведка', 'расследование', 'dox']):
                categories['osint'].append(group_info)
            elif any(word in title for word in ['спорт', 'футбол', 'хоккей', 'матч']):
                categories['спорт'].append(group_info)
            elif any(word in title for word in ['бизнес', 'стартап', 'инвестиции']):
                categories['бизнес'].append(group_info)
            elif any(word in title for word in ['новости', 'политика']):
                categories['новости'].append(group_info)
            elif any(word in title for word in ['юмор', 'прикол', 'мем', 'шутк']):
                categories['юмор'].append(group_info)
            else:
                categories['другое'].append(group_info)
        return dict(categories)
    def _analyze_time_patterns(self, messages):
        time_slots = {'утро (6-12)': 0, 'день (12-18)': 0, 'вечер (18-24)': 0, 'ночь (0-6)': 0}
        for msg in messages:
            date_str = msg.get('date', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    hour = dt.hour
                    if 6 <= hour < 12:
                        time_slots['утро (6-12)'] += 1
                    elif 12 <= hour < 18:
                        time_slots['день (12-18)'] += 1
                    elif 18 <= hour < 24:
                        time_slots['вечер (18-24)'] += 1
                    else:
                        time_slots['ночь (0-6)'] += 1
                except:
                    continue
        total = sum(time_slots.values())
        if total > 0:
            for slot in time_slots:
                time_slots[slot] = round(time_slots[slot] / total * 100, 1)
        most_active = max(time_slots.items(), key=lambda x: x[1]) if total > 0 else ('неизвестно', 0)
        return {
            'distribution': time_slots,
            'most_active': most_active[0],
            'active_percent': most_active[1]
        }
    def gct(self, user_id, stats_data, groups_data, messages):
        text = ""
        interests = self.analyze_interests(messages)
        personality = self.analyze_personality(messages)
        social_connections = self.analyze_social_connections(messages, user_id)
        osint_analysis = self.analyze_osint_doxxing_interest(messages)
        data_leaks = self.analyze_personal_data_leaks(messages)
        social_behavior = self.analyze_social_behavior(groups_data, messages)
        text += "ОСНОВНАЯ СТАТИСТИКА:\n"
        text += "-" * 20 + "\n"
        text += f"Имя: {stats_data.get('first_name', 'Неизвестно')} {stats_data.get('last_name', '')}\n"
        text += f"Бот: {'Да' if stats_data.get('is_bot') else 'Нет'}\n"
        text += f"Активен: {'Да' if stats_data.get('is_active') else 'Нет'}\n"
        text += f"Всего сообщений: {stats_data.get('total_msg_count', 0):,}\n"
        text += f"Сообщений в группах: {stats_data.get('msg_in_groups_count', 0):,}\n"
        text += f"Админ в группах: {stats_data.get('adm_in_groups', 0)}\n"
        text += f"Всего групп: {stats_data.get('total_groups', 0)}\n"
        text += f"Первое сообщение: {format_short_date(stats_data.get('first_msg_date'))}\n"
        text += f"Последнее сообщение: {format_short_date(stats_data.get('last_msg_date'))}\n"
        text += "АНАЛИЗ ИНТЕРЕСОВ:\n"
        text += "-" * 20 + "\n"
        for i, (interest, data) in enumerate(list(interests.items())[:9999], 1):
            text += f"{i}. {interest.upper()}:\n"
            text += f"   Активность: {data['score']} упоминаний\n"
            text += f"   Интенсивность: {data['intensity']}\n"
            text += f"   Охват темы: {data['percentage']}%\n"
            if data['keywords']:
                text += f"   Ключевые слова: {', '.join(data['keywords'][:9999])}\n"
            text += "\n"
        text += "ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ:\n"
        text += "-" * 20 + "\n"
        text += f"Основной тип: {personality['personality_type']}\n"
        text += f"Эмоциональный тон: {personality['emotional_tone']}\n"
        text += f"Характерные черты:\n"
        for trait, data in personality['dominant_traits']:
            text += f"   • {trait.capitalize()} ({data['intensity']}): {data['score']} индикаторов\n"
        text += "\n"
        text += "СОЦИАЛЬНЫЕ СВЯЗИ:\n"
        text += "-" * 20 + "\n"
        text += f"Всего уникальных упоминаний: {social_connections['total_unique_mentions']}\n"
        text += f"Топ упоминаемых пользователей:\n"
        for i, (username, count) in enumerate(social_connections['top_mentioned_users'][:9999], 1):
            text += f"   {i}. @{username}: {count} упоминаний\n"
        text += f"\nСамые активные чаты:\n"
        for i, (chat, count) in enumerate(social_connections['most_active_chats'][:3], 1):
            text += f"   {i}. {chat}: {count} сообщений\n"
        text += "\n"
        text += "OSINT/DOXXING АНАЛИЗ:\n"
        text += "-" * 20 + "\n"
        text += f"Уровень интереса: {osint_analysis['interest_level']}\n"
        text += f"Уровень риска: {osint_analysis['risk_level']}\n"
        text += f"OSINT score: {osint_analysis['osint_score']}/10\n"
        if osint_analysis['found_keywords']:
            text += f"Найденные ключевые слова: {', '.join(osint_analysis['found_keywords'])}\n"
        text += "\n"
        text += "АНАЛИЗ УТЕЧЕК ДАННЫХ:\n"
        text += "-" * 20 + "\n"
        total_leaks = sum(len(leaks) for leaks in data_leaks.values())
        text += f"Всего находок: {total_leaks}\n"
        if data_leaks['phones']:
            text += f"Найдено телефонов: {len(data_leaks['phones'])}\n"
            for phone in data_leaks['phones'][:9999]:
                text += f"   • {phone}\n"
        if data_leaks['emails']:
            text += f"Найдено email: {len(data_leaks['emails'])}\n"
            for email in data_leaks['emails'][:9999]:
                text += f"   • {email}\n"
        if data_leaks['cards']:
            text += f"Найдено карт: {len(data_leaks['cards'])}\n"
        if data_leaks['addresses']:
            text += f"Найдено адресов: {len(data_leaks['addresses'])}\n"
            for addr in data_leaks['addresses'][:9999]:
                text += f"   • {addr}\n"
        text += "\n"
        text += "СОЦИАЛЬНОЕ ПОВЕДЕНИЕ:\n"
        text += "-" * 20 + "\n"
        text += f"Всего групп: {social_behavior['total_groups']}\n"
        text += f"Активных групп: {social_behavior['active_groups']}\n"
        text += f"Уровень социальности: {social_behavior['social_level']}\n"
        text += f"Распределение по категориям:\n"
        for category, groups in list(social_behavior['group_categories'].items())[:9999]:
            if groups:
                active_count = len([g for g in groups if g['messages_count'] > 0])
                text += f"   {category}: {len(groups)} групп ({active_count} активных)\n"
        text += "\n"
        text += "АНАЛИЗ АКТИВНОСТИ:\n"
        text += "-" * 20 + "\n"
        for time_slot, percent in social_behavior['time_patterns']['distribution'].items():
            text += f"   {time_slot}: {percent}%\n"
        text += f"Пик активности: {social_behavior['time_patterns']['most_active']} ({social_behavior['time_patterns']['active_percent']}%)\n"
        text += "ВЫВОДЫ:\n"
        text += "-" * 20 + "\n"
        conclusions = self._generate_detailed_conclusions(interests, personality, social_connections, osint_analysis, data_leaks)
        for i, conclusion in enumerate(conclusions, 1):
            text += f"{i}. {conclusion}\n"
        raw_for_diagram = {
            "user_id": user_id,
            "stats": stats_data,
            "groups": groups_data['data'] if groups_data else [],
            "messages": messages,
            "leaks": data_leaks,
            "interests": interests,
            "personality": personality
        }
        return text, raw_for_diagram
    def _generate_detailed_conclusions(self, interests, personality, social_connections, osint_analysis, data_leaks):
        conclusions = []
        top_interests = list(interests.keys())[:3]
        if top_interests:
            interests_str = ", ".join(top_interests)
            conclusions.append(f"Основные сферы интересов: {interests_str}")
            if 'osint' in interests or 'doxxing' in interests:
                conclusions.append("Проявляет активный интерес к OSINT/Doxxing инструментам")
            if 'кибербезопасность' in interests:
                conclusions.append("Интересуется кибербезопасностью и техническими аспектами")
        personality_type = personality['personality_type']
        if personality_type == 'Экстраверт':
            conclusions.append("Высоко социально активен, легко заводит контакты")
        elif personality_type == 'Интроверт':
            conclusions.append("Избирателен в общении, предпочитает узкий круг")
        if social_connections['total_unique_mentions'] > 50:
            conclusions.append("Имеет широкий круг общения, много социальных контактов")
        elif social_connections['total_unique_mentions'] < 10:
            conclusions.append("Ограниченный круг общения, немного контактов")
        if osint_analysis['risk_level'] == 'высокий':
            conclusions.append("ВЫСОКИЙ РИСК: Активно интересуется OSINT/Doxxing инструментами")
        elif osint_analysis['risk_level'] == 'средний':
            conclusions.append("Средний интерес к инструментам разведки")
        total_leaks = sum(len(leaks) for leaks in data_leaks.values())
        if total_leaks > 0:
            conclusions.append(f"Обнаружены потенциальные утечки данных: {total_leaks} находок")
        if any(trait[0] in ['агрессивный', 'пессимист'] for trait in personality['dominant_traits']):
            conclusions.append("Склонен к негативным эмоциям и агрессивному поведению")
        if any(trait[0] in ['дружелюбный', 'оптимист'] for trait in personality['dominant_traits']):
            conclusions.append("Позитивно настроен, дружелюбен в общении")
        return conclusions[:8]

ai_analyzer = AIAccountAnalyzer()

async def show_ai_analysis(user_id):
    try:
        stats_data = await get_user_stats(user_id)
        if not stats_data:
            return f"[ERROR] Не удалось получить статистику", {}
        groups_data = await get_user_groups(user_id)
        if not groups_data:
            return f"[ERROR] Не удалось получить данные о группах", {}
        messages_data = await get_user_messages(user_id, 1, 1000)
        if not messages_data or not messages_data.get('data'):
            return f"[ERROR] Не удалось получить сообщения для анализа", {}
        text, raw = ai_analyzer.gct(
            user_id, stats_data, groups_data, messages_data['data']
        )
        return text, raw
    except Exception as e:
        return f"[ERROR] Ошибка AI анализа: {str(e)}", {}

# === 🔒 БЕЗОПАСНЫЕ JS API ===
class AuthAPI:
    def validate_license(self, key: str):
        try:
            res = validate_license_key(key)
            return {k: str(v) if not isinstance(v, (bool, int, float, str, list, dict, type(None))) else v for k, v in res.items()}
        except Exception as e:
            return {"valid": False, "error": f"Internal: {e}", "label": "", "expires_at": ""}
    def unlock(self):
        return {"success": True}

class MainAPI:
    def __init__(self):
        self.api = Api()

    def _wrap(self, func, *args):
        try:
            res = func(*args)
            if not isinstance(res, dict):
                return {"success": False, "error": "Invalid return type"}
            clean = {}
            for k, v in res.items():
                if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                    clean[k] = v
                else:
                    clean[k] = str(v)
            return clean
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === ОСНОВНЫЕ JS-ФУНКЦИИ ===
    def search_username(self, u): return self._wrap(self.api.search_username, u)
    def email_search(self, e): return self._wrap(self.api.email_search, e)
    def vk_osint(self, q): return self._wrap(self.api.vk_osint, q)
    def lookup_ip(self, i): return self._wrap(self.api.lookup_ip, i)
    def lookup_hlr(self, n): return self._wrap(self.api.lookup_hlr, n)
    def search_reveng(self, q): return self._wrap(self.api.search_reveng, q)
    def generate_dorks(self, q): return self._wrap(self.api.generate_dorks, q)
    def database_search(self, k): return self._wrap(self.api.database_search, k)
    def phone_lookup(self, n): return self._wrap(self.api.phone_lookup, n)
    def enhanced_ip_lookup(self, i): return self._wrap(self.api.enhanced_ip_lookup, i)
    def domain_whois(self, d): return self._wrap(self.api.domain_whois, d)
    def leak_search(self, t, q): return self._wrap(self.api.leak_search, t, q)
    def mac_vendor_lookup(self, m): return self._wrap(self.api.mac_vendor_lookup, m)
    def depsearch_lookup(self, q): return self._wrap(self.api.depsearch_lookup, q)
    def generate_qr_code(self, t): return self._wrap(self.api.generate_qr_code, t)
    def generate_identity_card(self, n, a, ad, p, e): return self._wrap(self.api.generate_identity_card, n, a, ad, p, e)

    # === FUNSTAT JS EXPOSURE ===
    def funstat_resolve_username_js(self, username): return self._wrap(self.api.funstat_resolve_username, username)
    def funstat_username_usage_js(self, username): return self._wrap(self.api.funstat_username_usage, username)
    def funstat_user_stats_js(self, user_id): return self._wrap(self.api.funstat_user_stats, int(user_id))
    def funstat_user_messages_js(self, user_id, media_filter): return self._wrap(self.api.funstat_user_messages, int(user_id), media_filter)
    def funstat_user_groups_js(self, user_id): return self._wrap(self.api.funstat_user_groups, int(user_id))
    def funstat_user_reputation_js(self, user_id): return self._wrap(self.api.funstat_user_reputation, int(user_id))
    def funstat_text_search_js(self, query): return self._wrap(self.api.funstat_text_search, query)
    def funstat_ai_analysis_js(self, user_id): return self._wrap(self.api.funstat_ai_analysis, int(user_id))

    # === BIGBASE + УНИВЕРСАЛЬНЫЙ ПОИСК ===
    def bigbase_search_universal_js(self, q): return self._wrap(self.api.bigbase_search, q)
    def funstat_search_username_js(self, u): return self._wrap(self.api.funstat_search_username, u)

    # === 🔹 НОВЫЙ: ФОТО-ПОИСК ===
    def search_faces_js(self, image_b64: str):
        return self._wrap(self.api.search_faces, image_b64)

    # === ДИАГРАММА ===
    def set_diagram_data(self, raw_data):
        try:
            nodes = []
            edges = []
            node_id_map = {}
            counter = 1

            # Корень: фото или query
            root_label = "📸 Photo Search"
            if raw_data.get('query'):
                root_label = raw_data['query']
            if raw_data.get('image_b64'):
                root_label = "🖼 Uploaded Photo"
            root_id = counter
            nodes.append({
                'id': root_id,
                'label': root_label,
                'shape': 'dot',
                'size': 25,
                'color': {
                    'background': '#4facfe',
                    'border': '#00f2fe',
                    'highlight': {
                        'background': '#00f2fe',
                        'border': '#ffffff'
                    }
                },
                'font': {'color': '#ffffff', 'size': 16, 'face': 'Segoe UI'},
                'shadow': {
                    'enabled': True,
                    'color': 'rgba(0,242,254,0.6)',
                    'size': 10,
                    'x': 0,
                    'y': 4
                }
            })
            node_id_map['root'] = root_id
            counter += 1

            # Photo results → names → cities
            if 'results' in raw_data and isinstance(raw_data['results'], list):
                for i, person in enumerate(raw_data['results'][:10]):
                    name = person.get('name', f"ID{person.get('vk_id', i+1)}")
                    similarity = person.get('similarity_rate', 0)
                    vk_id = str(person.get('vk_id', ''))
                    city = person.get('city', '')

                    # 👤 Имя
                    if name not in node_id_map:
                        node_id_map[name] = counter
                        nodes.append({
                            'id': counter,
                            'label': f"{name}\n({similarity}%)",
                            'shape': 'dot',
                            'size': 25,
                            'color': {
                                'background': '#e91e63',
                                'border': '#00f2fe',
                                'highlight': {
                                    'background': '#ff4081',
                                    'border': '#ffffff'
                                }
                            },
                            'font': {'color': '#ffffff', 'size': 14},
                            'shadow': {
                                'enabled': True,
                                'color': 'rgba(0,242,254,0.6)',
                                'size': 10,
                                'x': 0,
                                'y': 4
                            }
                        })
                        edges.append({'from': root_id, 'to': counter, 'label': 'match'})
                        counter += 1

                    # 🌆 Город
                    if city and city not in node_id_map:
                        node_id_map[city] = counter
                        nodes.append({
                            'id': counter,
                            'label': f"📍 {city}",
                            'shape': 'dot',
                            'size': 25,
                            'color': {
                                'background': '#e67e22',
                                'border': '#00f2fe',
                                'highlight': {
                                    'background': '#ff9800',
                                    'border': '#ffffff'
                                }
                            },
                            'font': {'color': '#ffffff', 'size': 14},
                            'shadow': {
                                'enabled': True,
                                'color': 'rgba(0,242,254,0.6)',
                                'size': 10,
                                'x': 0,
                                'y': 4
                            }
                        })
                        edges.append({'from': node_id_map[name], 'to': counter, 'label': 'city'})
                        counter += 1

            return {"success": True, "nodes": nodes, "edges": edges}
        except Exception as e:
            return {"success": False, "error": str(e)}

# === 🔥 FINAL HTML С ВКЛАДКОЙ «📸 Photo» И СТИЛИЗОВАННЫМИ КРУЖКАМИ ===
main_html_with_auth = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>OSINT Toolkit</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a1a35 0%, #1a3a6c 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
            padding: 0;
        }
        .starfall {
            position: fixed;
            top: -100px;
            left: -100px;
            width: calc(100% + 200px);
            height: calc(100% + 200px);
            pointer-events: none;
            overflow: hidden;
            z-index: 0;
        }
        .starfall span {
            position: absolute;
            background: #fff;
            border-radius: 50%;
            box-shadow: 0 0 8px 2px rgba(255, 255, 255, 0.8);
            animation: fallDiagonal 10s linear infinite;
            opacity: 0;
            animation-delay: var(--delay);
            animation-duration: var(--duration);
        }
        @keyframes fallDiagonal {
            0% { transform: translate(100vw, -100px) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translate(-100px, 100vh) rotate(360deg); opacity: 0; }
        }
        .container {
            position: relative;
            z-index: 10;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        #auth-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: rgba(10, 26, 53, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .auth-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 40px;
            width: 90%;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }
        .neon-title {
            font-size: 2.6em;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow:
                0 0 4px #00f2fe,
                0 0 8px #00f2fe,
                0 0 12px rgba(0, 242, 254, 0.8),
                0 0 16px rgba(79, 172, 254, 0.7),
                0 0 20px rgba(0, 242, 254, 0.5);
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            color: transparent;
            position: relative;
        }
        .subtitle {
            color: #a0d2ff;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .input-group input {
            width: 100%;
            padding: 14px 20px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            outline: none;
            transition: all 0.3s;
        }
        .input-group input:focus {
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.6);
        }
        button {
            width: auto;
            padding: 12px 20px;
            font-size: 15px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            color: #0a1a35;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
        }
        .error, .success {
            margin-top: 15px;
            font-size: 0.95em;
            min-height: 24px;
        }
        .error { color: #ff6b6b; }
        .success { color: #4dff91; }
        #main-content { display: none; }
        .header {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .tabs {
            display: flex;
            flex-wrap: nowrap;
            justify-content: center;
            gap: 6px;
            margin-bottom: 25px;
        }
        .tab-button {
            padding: 10px 18px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            white-space: nowrap;
            font-size: 15px;
        }
        .tab-button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        .tab-button.active {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            color: #0a1a35;
            box-shadow: 0 3px 10px rgba(79, 172, 254, 0.4);
        }
        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .tab-content.active { display: block; }
        .input-group { margin-bottom: 15px; }
        .input-group label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            color: #4facfe;
        }
        .button-row {
            display: flex;
            gap: 8px;
            justify-content: flex-start;
            margin-bottom: 15px;
        }
        .result-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }
        .json-pane {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
            border-left: 3px solid #4facfe;
        }
        .diagram-pane {
            height: 500px;
            background: rgba(10, 26, 53, 0.3);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }
        .subtabs {
            display: flex;
            gap: 6px;
            margin-bottom: 15px;
        }
        .subtab-button {
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 6px;
            color: #fff;
            cursor: pointer;
            font-size: 14px;
        }
        .subtab-button.active {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            color: #0a1a35;
        }
        .funstat-content { display: none; }
        .funstat-content.active { display: block; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }
        .card h3 {
            color: #4facfe;
            margin-bottom: 12px;
            font-size: 1.1em;
        }
        .card input {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: none;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            outline: none;
            transition: all 0.3s;
        }
        .card input:focus {
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.6);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 15px 0;
        }
        .loading-spinner {
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 2px solid #4facfe;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        /* 🔹 Photo preview */
        #photo-preview-container {
            margin: 15px 0;
            text-align: center;
        }
        #photo-preview {
            max-width: 300px;
            max-height: 300px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: none;
        }
    </style>
</head>
<body>
    <!-- 🔐 Авторизация -->
    <div id="auth-overlay">
        <div class="starfall" id="auth-starfall"></div>
        <div class="auth-box">
            <div class="neon-title">🧊 Arasaka</div>
            <div class="subtitle">Enter your access key to continue</div>
            <div class="input-group">
                <input type="text" id="license-key" placeholder="e.g. A1b2C3d4E5f6DAY" autocomplete="off">
            </div>
            <button onclick="validate()">Unlock Toolkit</button>
            <div id="message" class="error"></div>
        </div>
    </div>
    <!-- 🧊 Основной интерфейс -->
    <div id="main-content" class="container">
        <div class="header">
            <h1 class="neon-title">🧊 Arasaka Project</h1>
            <p>arasaka - наблюдение это искусство..</p>
        </div>
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('username-tab')">👤 Username</button>
            <button class="tab-button" onclick="showTab('email-tab')">📧 Email</button>
            <button class="tab-button" onclick="showTab('phone-tab')">📞 Phone</button>
            <button class="tab-button" onclick="showTab('ip-tab')">🌐 IP</button>
            <button class="tab-button" onclick="showTab('vk-tab')">🔍 VK OSINT</button>
            <button class="tab-button" onclick="showTab('funstat-tab')">📊 Stat</button>
            <button class="tab-button" onclick="showTab('domain-tab')">🌍 Domain</button>
            <button class="tab-button" onclick="showTab('dork-tab')">🔎 Dorks</button>
            <button class="tab-button" onclick="showTab('database-tab')">💾 Database</button>
            <button class="tab-button" onclick="showTab('tools-tab')">🛠️ Tools</button>
            <button class="tab-button" onclick="showTab('photo-tab')">📸 Photo</button>
        </div>

        <!-- ... другие вкладки (username-tab, email-tab и т.д.) — без изменений ... -->

        <!-- 🔹 Photo tab -->
        <div id="photo-tab" class="tab-content">
            <div class="input-group">
                <label>Upload Photo (JPG/PNG):</label>
                <input type="file" id="photo-input" accept="image/jpeg,image/png" onchange="previewImage(this)">
            </div>
            <div class="button-row">
                <button onclick="searchFaces()">🔍 Search Faces</button>
            </div>
            <div id="photo-preview-container">
                <img id="photo-preview">
            </div>
            <div class="loading" id="photo-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="photo-result"></div>
                <div class="diagram-pane" id="photo-diagram"></div>
            </div>
        </div>

        <!-- USERNAME TAB -->
        <div id="username-tab" class="tab-content active">
            <div class="input-group"><label>Username:</label><input type="text" id="username"></div>
            <div class="button-row">
                <button onclick="searchUsername()">Search Username</button>
            </div>
            <div class="loading" id="username-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="username-result"></div>
                <div class="diagram-pane" id="username-diagram"></div>
            </div>
        </div>

        <!-- EMAIL TAB -->
        <div id="email-tab" class="tab-content">
            <div class="input-group"><label>Email:</label><input type="email" id="email"></div>
            <div class="button-row">
                <button onclick="searchEmail()">Check Email</button>
                <button onclick="searchEmailBigBase()">🔍 more</button>
            </div>
            <div class="loading" id="email-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="email-result"></div>
                <div class="diagram-pane" id="email-diagram"></div>
            </div>
        </div>

        <!-- PHONE TAB -->
        <div id="phone-tab" class="tab-content">
            <div class="input-group"><label>Phone:</label><input type="text" id="phone"></div>
            <div class="button-row">
                <button onclick="lookupPhone()">Lookup Phone</button>
                <button onclick="searchPhoneBigBase()">🔍 more</button>
            </div>
            <div class="loading" id="phone-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="phone-result"></div>
                <div class="diagram-pane" id="phone-diagram"></div>
            </div>
        </div>

        <!-- IP TAB -->
        <div id="ip-tab" class="tab-content">
            <div class="input-group"><label>IP:</label><input type="text" id="ip"></div>
            <div class="button-row">
                <button onclick="lookupIP()">Lookup IP</button>
                <button onclick="searchIPBigBase()">🔍 more</button>
            </div>
            <div class="loading" id="ip-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="ip-result"></div>
                <div class="diagram-pane" id="ip-diagram"></div>
            </div>
        </div>

        <!-- VK TAB -->
        <div id="vk-tab" class="tab-content">
            <div class="input-group"><label>VK:</label><input type="text" id="vk-query"></div>
            <div class="button-row">
                <button onclick="vkOsint()">Analyze VK Profile</button>
            </div>
            <div class="loading" id="vk-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="vk-result"></div>
                <div class="diagram-pane" id="vk-diagram"></div>
            </div>
        </div>

        <!-- FUNSTAT TAB -->
        <div id="funstat-tab" class="tab-content">
            <div class="subtabs">
                <button class="subtab-button active" onclick="showFunStatTab('search')">🔍 Поиск</button>
                <button class="subtab-button" onclick="showFunStatTab('stats')">📊 Статистика</button>
                <button class="subtab-button" onclick="showFunStatTab('messages')">💬 Сообщения</button>
                <button class="subtab-button" onclick="showFunStatTab('groups')">👥 Группы</button>
                <button class="subtab-button" onclick="showFunStatTab('reputation')">⭐ Репутация</button>
                <button class="subtab-button" onclick="showFunStatTab('text')">🔤 Текст</button>
                <button class="subtab-button" onclick="showFunStatTab('ai')">🧠 AI Анализ</button>
            </div>
            <div id="funstat-search" class="funstat-content active">
                <div class="input-group"><label>Username (без @):</label><input type="text" id="funstat-username"></div>
                <div class="button-row"><button onclick="funstatResolveUsername()">🔍 Получить ID</button></div>
                <div class="json-pane" id="funstat-resolve-result"></div>
                <br>
                <div class="input-group"><label>Username для истории использования:</label><input type="text" id="funstat-usage-username"></div>
                <div class="button-row"><button onclick="funstatUsernameUsage()">📁 История использования</button></div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-usage-result"></div>
                    <div class="diagram-pane" id="funstat-usage-diagram"></div>
                </div>
            </div>
            <div id="funstat-stats" class="funstat-content">
                <div class="input-group"><label>ID пользователя:</label><input type="number" id="funstat-user-id-stats"></div>
                <div class="button-row"><button onclick="funstatUserStats()">📊 Статистика</button></div>
                <div class="loading" id="funstat-stats-loading"><div class="loading-spinner"></div></div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-stats-result"></div>
                    <div class="diagram-pane" id="funstat-stats-diagram"></div>
                </div>
            </div>
            <div id="funstat-messages" class="funstat-content">
                <div class="input-group"><label>ID пользователя:</label><input type="number" id="funstat-user-id-msg"></div>
                <div class="button-row">
                    <button onclick="funstatUserMessages('all')">💬 Все</button>
                    <button onclick="funstatUserMessages('1')">🖼 Фото</button>
                    <button onclick="funstatUserMessages('2')">🎥 Видео</button>
                    <button onclick="funstatUserMessages('3')">🎵 Аудио</button>
                    <button onclick="funstatUserMessages('4')">📎 Файлы</button>
                    <button onclick="funstatUserMessages('10')">🖼 Стикеры</button>
                    <button onclick="funstatUserMessages('5')">📍 Гео</button>
                    <button onclick="funstatUserMessages('6')">📇 Контакты</button>
                    <button onclick="funstatUserMessages('7')">⭕ Кружки</button>
                </div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-msg-result"></div>
                    <div class="diagram-pane" id="funstat-msg-diagram"></div>
                </div>
            </div>
            <div id="funstat-groups" class="funstat-content">
                <div class="input-group"><label>ID пользователя:</label><input type="number" id="funstat-user-id-groups"></div>
                <div class="button-row"><button onclick="funstatUserGroups()">👥 Группы</button></div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-groups-result"></div>
                    <div class="diagram-pane" id="funstat-groups-diagram"></div>
                </div>
            </div>
            <div id="funstat-reputation" class="funstat-content">
                <div class="input-group"><label>ID пользователя:</label><input type="number" id="funstat-user-id-rep"></div>
                <div class="button-row"><button onclick="funstatUserReputation()">⭐ Репутация</button></div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-rep-result"></div>
                    <div class="diagram-pane" id="funstat-rep-diagram"></div>
                </div>
            </div>
            <div id="funstat-text" class="funstat-content">
                <div class="input-group"><label>Текст для поиска:</label><input type="text" id="funstat-search-text"></div>
                <div class="button-row"><button onclick="funstatTextSearch()">🔤 Поиск по тексту</button></div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-text-result"></div>
                    <div class="diagram-pane" id="funstat-text-diagram"></div>
                </div>
            </div>
            <div id="funstat-ai" class="funstat-content">
                <div class="input-group"><label>ID пользователя:</label><input type="number" id="funstat-user-id-ai"></div>
                <div class="button-row"><button onclick="funstatAIAnalysis()">🧠 AI-Анализ</button></div>
                <div class="loading" id="funstat-ai-loading"><div class="loading-spinner"></div></div>
                <div class="result-container">
                    <div class="json-pane" id="funstat-ai-result"></div>
                    <div class="diagram-pane" id="funstat-ai-diagram"></div>
                </div>
            </div>
        </div>

        <!-- DOMAIN TAB -->
        <div id="domain-tab" class="tab-content">
            <div class="input-group"><label>Domain:</label><input type="text" id="domain"></div>
            <div class="button-row"><button onclick="domainWhois()">WHOIS Lookup</button></div>
            <div class="loading" id="domain-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="domain-result"></div>
                <div class="diagram-pane" id="domain-diagram"></div>
            </div>
        </div>

        <!-- DORKS TAB -->
        <div id="dork-tab" class="tab-content">
            <div class="input-group"><label>Query:</label><input type="text" id="dork-query"></div>
            <div class="button-row"><button onclick="generateDorks()">Generate Dorks</button></div>
            <div class="loading" id="dork-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="dork-result"></div>
                <div class="diagram-pane" id="dork-diagram"></div>
            </div>
        </div>

        <!-- DATABASE TAB -->
        <div id="database-tab" class="tab-content">
            <div class="input-group"><label>Keyword:</label><input type="text" id="db-keyword"></div>
            <div class="button-row"><button onclick="searchDatabase()">Search Database</button></div>
            <div class="loading" id="db-loading"><div class="loading-spinner"></div></div>
            <div class="result-container">
                <div class="json-pane" id="db-result"></div>
                <div class="diagram-pane" id="db-diagram"></div>
            </div>
        </div>

        <!-- TOOLS TAB -->
        <div id="tools-tab" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h3>QR Code</h3>
                    <input type="text" id="qr-text" placeholder="Text to encode">
                    <button onclick="generateQR()">Generate</button>
                    <div id="qr-result"></div>
                </div>
                <div class="card">
                    <h3>Identity Card</h3>
                    <input type="text" id="id-name" placeholder="Name">
                    <input type="text" id="id-age" placeholder="Age">
                    <input type="text" id="id-address" placeholder="Address">
                    <input type="text" id="id-phone" placeholder="Phone">
                    <input type="text" id="id-email" placeholder="Email">
                    <button onclick="generateID()">Generate</button>
                    <div id="id-result"></div>
                </div>
                <div class="card">
                    <h3>MAC Lookup</h3>
                    <input type="text" id="mac-address" placeholder="e.g. 00:1A:2B:3C:4D:5E">
                    <button onclick="lookupMAC()">Lookup</button>
                    <div class="json-pane" id="mac-result" style="max-height:150px;"></div>
                </div>
                <div class="card">
                    <h3>Load Test</h3>
                    <input type="text" id="load-target" placeholder="Target IP">
                    <input type="number" id="load-port" value="80" min="1" max="65535">
                    <input type="number" id="load-threads" value="10" min="1">
                    <input type="number" id="load-duration" value="10" min="1">
                    <button onclick="runLoadTest()">Run</button>
                    <div class="json-pane" id="load-result" style="max-height:150px;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let networks = {};
        document.addEventListener('DOMContentLoaded', () => {
            // Starfall
            const starfall = document.createElement('div');
            starfall.className = 'starfall';
            document.body.appendChild(starfall);
            for (let i = 0; i < 150; i++) {
                const star = document.createElement('span');
                star.style.left = (Math.random() * 200 - 50) + '%';
                star.style.top = (Math.random() * 200 - 50) + '%';
                star.style.setProperty('--delay', Math.random() * 15 + 's');
                star.style.setProperty('--duration', (7 + Math.random() * 10) + 's');
                const size = 1 + Math.random() * 3;
                star.style.width = star.style.height = size + 'px';
                starfall.appendChild(star);
            }
            const authStarfall = document.getElementById('auth-starfall');
            for (let i = 0; i < 80; i++) {
                const star = document.createElement('span');
                star.style.left = (Math.random() * 200 - 50) + '%';
                star.style.top = (Math.random() * 200 - 50) + '%';
                star.style.setProperty('--delay', Math.random() * 15 + 's');
                star.style.setProperty('--duration', (5 + Math.random() * 8) + 's');
                const size = 1 + Math.random() * 2;
                star.style.width = star.style.height = size + 'px';
                authStarfall.appendChild(star);
            }

            // Init networks
            const diagramIds = [
                'username-diagram', 'email-diagram', 'phone-diagram', 'ip-diagram', 'vk-diagram',
                'funstat-usage-diagram', 'funstat-stats-diagram', 'funstat-msg-diagram',
                'funstat-groups-diagram', 'funstat-rep-diagram', 'funstat-text-diagram', 'funstat-ai-diagram',
                'domain-diagram', 'dork-diagram', 'db-diagram', 'photo-diagram'
            ];
            diagramIds.forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    const data = { nodes: new vis.DataSet(), edges: new vis.DataSet() };
                    const options = {
                        nodes: {
                            shape: 'dot',
                            size: 25,
                            borderWidth: 2,
                            shadow: {
                                enabled: true,
                                color: 'rgba(0,242,254,0.6)',
                                size: 10,
                                x: 0,
                                y: 4
                            },
                            color: {
                                background: '#0a1a35',
                                border: '#4facfe',
                                highlight: {
                                    background: '#4facfe',
                                    border: '#00f2fe'
                                }
                            },
                            font: {
                                color: '#ffffff',
                                size: 16,
                                face: 'Segoe UI'
                            }
                        },
                        edges: {
                            color: { color: '#aaa', highlight: '#e74c3c' },
                            width: 2,
                            smooth: { type: 'dynamic' },
                            shadow: true
                        },
                        physics: {
                            enabled: true,
                            barnesHut: {
                                gravitationalConstant: -30000,
                                springLength: 180,
                                springConstant: 0.04
                            },
                            stabilization: { iterations: 150 }
                        },
                        interaction: {
                            hover: true,
                            tooltipDelay: 100,
                            navigationButtons: true,
                            keyboard: true
                        }
                    };
                    networks[id] = new vis.Network(el, data, options);
                }
            });
        });

        function showTab(id) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function showFunStatTab(subtabId) {
            document.querySelectorAll('.funstat-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.subtab-button').forEach(el => el.classList.remove('active'));
            document.getElementById('funstat-' + subtabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function showLoading(id) { document.getElementById(id).style.display = 'block'; }
        function hideLoading(id) { document.getElementById(id).style.display = 'none'; }

        function displayResult(id, data) {
            const jsonPane = document.getElementById(id);
            if (data.success) {
                const pre = document.createElement('pre');
                let text = typeof data.text === 'string' ? data.text :
                           typeof data.results === 'string' ? data.results :
                           JSON.stringify(data.results || data.text || data, null, 2);
                pre.textContent = text;
                jsonPane.innerHTML = '';
                jsonPane.appendChild(pre);

                // Diagram
                const diagramId = id.replace('-result', '-diagram');
                const network = networks[diagramId];
                if (network && data.raw) {
                    pywebview.api.set_diagram_data(data.raw).then(dres => {
                        if (dres.success) {
                            const nodes = new vis.DataSet(dres.nodes);
                            const edges = new vis.DataSet(dres.edges);
                            network.setData({nodes, edges});
                            network.fit();
                        }
                    }).catch(console.warn);
                }
            } else {
                jsonPane.innerHTML = `<pre style="color:#ff6b6b;">Error: ${data.error || 'Unknown'}</pre>`;
                const diagramId = id.replace('-result', '-diagram');
                const network = networks[diagramId];
                if (network) {
                    network.setData({nodes: new vis.DataSet(), edges: new vis.DataSet()});
                }
            }
        }

        async function _call(method, inputId, resultId, loadingId = 'none') {
            const el = document.getElementById(inputId);
            const val = el ? el.value : null;
            if (!val) return alert('Input required');
            if (loadingId !== 'none') showLoading(loadingId);
            try {
                const res = await pywebview.api[method](val);
                displayResult(resultId, res);
            } catch (e) {
                displayResult(resultId, {success: false, error: e.message});
            }
            if (loadingId !== 'none') hideLoading(loadingId);
        }

        // Basic search
        async function searchUsername() { await _call('search_username', 'username', 'username-result', 'username-loading'); }
        async function searchEmail() { await _call('email_search', 'email', 'email-result', 'email-loading'); }
        async function searchEmailBigBase() { await _call('bigbase_search_universal_js', 'email', 'email-result', 'email-loading'); }
        async function lookupPhone() { await _call('phone_lookup', 'phone', 'phone-result', 'phone-loading'); }
        async function searchPhoneBigBase() { await _call('bigbase_search_universal_js', 'phone', 'phone-result', 'phone-loading'); }
        async function lookupIP() { await _call('enhanced_ip_lookup', 'ip', 'ip-result', 'ip-loading'); }
        async function searchIPBigBase() { await _call('bigbase_search_universal_js', 'ip', 'ip-result', 'ip-loading'); }
        async function vkOsint() { await _call('vk_osint', 'vk-query', 'vk-result', 'vk-loading'); }
        async function domainWhois() { await _call('domain_whois', 'domain', 'domain-result', 'domain-loading'); }
        async function generateDorks() { await _call('generate_dorks', 'dork-query', 'dork-result', 'dork-loading'); }
        async function searchDatabase() { await _call('database_search', 'db-keyword', 'db-result', 'db-loading'); }
        async function lookupMAC() { await _call('mac_vendor_lookup', 'mac-address', 'mac-result'); }
        async function runLoadTest() {
            const ip = document.getElementById('load-target').value,
                  port = document.getElementById('load-port').value,
                  threads = document.getElementById('load-threads').value,
                  dur = document.getElementById('load-duration').value;
            if (!ip || !port || !threads || !dur) return alert('All fields required');
            try {
                const res = await pywebview.api.run_load_test(ip, port, threads, dur);
                displayResult('load-result', res);
            } catch (e) { alert('Load Test Error: ' + e.message); }
        }

        // FunStat
        async function funstatResolveUsername() { await _call('funstat_resolve_username_js', 'funstat-username', 'funstat-resolve-result'); }
        async function funstatUsernameUsage() { await _call('funstat_username_usage_js', 'funstat-usage-username', 'funstat-usage-result'); }
        async function funstatUserStats() { await _call('funstat_user_stats_js', 'funstat-user-id-stats', 'funstat-stats-result', 'funstat-stats-loading'); }
        async function funstatUserMessages(media_filter) {
            const userId = document.getElementById('funstat-user-id-msg').value;
            if (!userId) return alert('ID required');
            try {
                const res = await pywebview.api.funstat_user_messages_js(userId, media_filter);
                displayResult('funstat-msg-result', res);
            } catch (e) { displayResult('funstat-msg-result', {success: false, error: e.message}); }
        }
        async function funstatUserGroups() { await _call('funstat_user_groups_js', 'funstat-user-id-groups', 'funstat-groups-result'); }
        async function funstatUserReputation() { await _call('funstat_user_reputation_js', 'funstat-user-id-rep', 'funstat-rep-result'); }
        async function funstatTextSearch() { await _call('funstat_text_search_js', 'funstat-search-text', 'funstat-text-result'); }
        async function funstatAIAnalysis() { await _call('funstat_ai_analysis_js', 'funstat-user-id-ai', 'funstat-ai-result', 'funstat-ai-loading'); }

        // Tools
        async function generateQR() {
            const t = document.getElementById('qr-text').value;
            if (!t) return alert('Text required');
            try {
                const res = await pywebview.api.generate_qr_code(t);
                document.getElementById('qr-result').innerHTML = res.success 
                    ? `<img src="${res.qr_code}" alt="QR" style="max-width:200px;margin:10px auto;display:block;">`
                    : `<p style="color:#ff6b6b;">${res.error}</p>`;
            } catch (e) { alert('QR Error: ' + e.message); }
        }
        async function generateID() {
            const n = document.getElementById('id-name').value,
                  a = document.getElementById('id-age').value,
                  ad = document.getElementById('id-address').value,
                  p = document.getElementById('id-phone').value,
                  e = document.getElementById('id-email').value;
            if (!n || !a || !ad || !p || !e) return alert('All fields required');
            try {
                const res = await pywebview.api.generate_identity_card(n, a, ad, p, e);
                document.getElementById('id-result').innerHTML = res.success 
                    ? `<img src="${res.id_card}" alt="ID" style="max-width:200px;margin:10px auto;display:block;">`
                    : `<p style="color:#ff6b6b;">${res.error}</p>`;
            } catch (e) { alert('ID Error: ' + e.message); }
        }

        // 🔹 PHOTO SEARCH JS
        function previewImage(input) {
            const preview = document.getElementById('photo-preview');
            preview.style.display = 'none';
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'inline-block';
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        async function searchFaces() {
            const input = document.getElementById('photo-input');
            if (!input.files || !input.files[0]) {
                return alert('⚠️ Please select an image file.');
            }
            const file = input.files[0];
            if (!file.type.match('image.*')) {
                return alert('⚠️ Only image files (JPG/PNG) allowed.');
            }
            const reader = new FileReader();
            reader.onload = async function() {
                const b64 = reader.result;
                showLoading('photo-loading');
                try {
                    const res = await pywebview.api.search_faces_js(b64);
                    displayResult('photo-result', res);
                } catch (e) {
                    displayResult('photo-result', {success: False, error: e.message});
                }
                hideLoading('photo-loading');
            };
            reader.readAsDataURL(file);
        }

        // Auth
        async function validate() {
            const key = document.getElementById('license-key').value.trim();
            const msg = document.getElementById('message');
            if (!key) {
                msg.className = 'error';
                msg.textContent = '⚠️ Key is empty.';
                return;
            }
            try {
                const res = await pywebview.api.validate_license(key);
                if (res.valid) {
                    msg.className = 'success';
                    msg.textContent = `✅ ${res.label}-license valid until: ${res.expires_at}`;
                    setTimeout(() => {
                        document.getElementById('auth-overlay').style.display = 'none';
                        document.getElementById('main-content').style.display = 'block';
                    }, 1000);
                } else {
                    msg.className = 'error';
                    msg.textContent = '❌ ' + (res.error || 'Invalid key.');
                }
            } catch (e) {
                msg.className = 'error';
                msg.textContent = '🚨 JS API Error: ' + (e.message || e);
            }
        }
        document.getElementById('license-key').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') validate();
        });
    </script>
</body>
</html>
'''

def start_main_window():
    auth_api = AuthAPI()
    main_api = MainAPI()
    window = webview.create_window(
        'Arasaka Toolkit',
        html=main_html_with_auth,
        js_api=main_api,
        width=1300,
        height=850,
        min_size=(900, 600),
        background_color='#0a1a35'
    )
    window.expose(auth_api.validate_license)
    webview.start(debug=False)

if __name__ == '__main__':
    start_main_window()
