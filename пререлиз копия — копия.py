import webview
import requests
import re
import json
import asyncio
import aiohttp
import random
import socket
import whois
import os
import sys
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


try:
    from fake_useragent import UserAgent
    def get_random_user_agent():
        return UserAgent().random
except ImportError:
    def get_random_user_agent():
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

HLR_API_URL = "https://www.ipqualityscore.com/api/json/phone"
HLR_API_KEY = "dbff5d449d30a6233ad09156cd2aab77"
DEPSEARCH_TOKEN = 'xxcdVyYgIvfEPXdDvhyknWOyy6qthJqn'
PHONE_API_KEY = 'b071233df03f4622e7affead6d13850c'
SHODAN_API_KEY = 'UJN4abrj0J8qLYvrp48bnWynNWI2wHpn'
IPINFO_API_KEY = '208e16c19a4708'
ABSTRACT_API_KEY = 'acfdcf46ccae49c1abb0e2aec8296999'

class HttpWebNumber:
    def __init__(self):
        self.__check_number_link = "https://htmlweb.ru/geo/api.php?json&telcod="
        self.__not_found_text = "No information"

    def lookup(self, user_number: str) -> dict:
        try:
            response = requests.get(
                self.__check_number_link + user_number,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=12
            )
            if response.ok:
                return response.json()
        except Exception:
            pass
        return {"status_error": True}

class Api:
    def __init__(self):
        self.print_lock = threading.Lock()
        self.files_searched_count = 0
        self.results_found_count = 0

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
        return {'success': True, 'username': username, 'results': results}

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
        if results:
            return {'success': True, 'email': email, 'results': results}
        return {'success': False, 'error': 'Email not found in leak DBs'}

    def vk_osint(self, query: str):
        try:
            # Получаем основную информацию
            user_info = self._get_vk_user_info(query)
            if not user_info:
                return {'success': False, 'error': 'User not found'}
            
            user_id = user_info.get('id', '')
            result = {
                'user_info': user_info,
                'posts': self._get_vk_user_posts(user_id),
                'friends': self._get_vk_friends(user_id),
                'groups': self._get_vk_groups(user_id),
            }
            
            # Форматируем результат для вывода
            formatted = self._format_vk_results(result)
            
            # Создаем файл для скачивания
            download_filename = f"vk_info_{query}.txt"
            with open(download_filename, 'w', encoding='utf-8') as f:
                f.write(formatted)
            
            return {
                'success': True,
                'formatted': formatted,
                'raw_data': result,
                'download_url': download_filename
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_vk_user_info(self, username: str):
        """Получение основной информации о пользователе через парсинг страницы"""
        url = f"https://vk.com/{username}"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем информацию из раздела "profile_info"
            profile_info = {}
            profile_block = soup.find('div', {'id': 'profile_info'})
            if profile_block:
                # Имя и фамилия
                name_element = profile_block.find('h1', class_='page_name')
                if name_element:
                    profile_info['name'] = name_element.get_text(strip=True)
                
                # Статус
                status_element = profile_block.find('div', class_='pp_status')
                if status_element:
                    profile_info['status'] = status_element.get_text(strip=True)
            
            # Извлекаем информацию из раздела "profile_info_rows"
            info_rows = soup.find_all('div', class_='profile_info_row')
            for row in info_rows:
                label = row.find('div', class_='label').get_text(strip=True) if row.find('div', class_='label') else 'Unknown'
                value = row.find('div', class_='labeled').get_text(strip=True) if row.find('div', class_='labeled') else ''
                profile_info[label] = value
            
            # Извлекаем количество подписчиков
            followers_element = soup.find('a', {'href': f'/{username}/followers'})
            if followers_element:
                followers_text = followers_element.find('span', class_='count').get_text(strip=True)
                profile_info['followers'] = followers_text
            
            # Извлекаем ID пользователя из скрытых полей
            user_id_input = soup.find('input', {'name': 'to_id'})
            if user_id_input and 'value' in user_id_input.attrs:
                profile_info['id'] = user_id_input['value']
            
            return profile_info
        except Exception as e:
            return {'error': str(e)}
    
    def _get_vk_user_posts(self, user_id: str):
        """Получение последних постов пользователя"""
        if not user_id:
            return []
        
        url = f"https://vk.com/wall{user_id}"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            posts = []
            post_blocks = soup.find_all('div', class_='_post_content')
            
            for post_block in post_blocks[:5]:  # Ограничиваемся 5 постами
                post = {}
                
                # Текст поста
                text_element = post_block.find('div', class_='wall_post_text')
                if text_element:
                    post['text'] = text_element.get_text(strip=True)
                
                # Дата поста
                date_element = post_block.find('span', class_='rel_date')
                if date_element:
                    post['date'] = date_element.get_text(strip=True)
                
                # Количество лайков
                likes_element = post_block.find('a', class_='like_btn_count')
                if likes_element:
                    post['likes'] = likes_element.get_text(strip=True)
                
                # Количество репостов
                reposts_element = post_block.find('a', class_='share_btn_count')
                if reposts_element:
                    post['reposts'] = reposts_element.get_text(strip=True)
                
                if post:
                    posts.append(post)
            
            return posts
        except:
            return []
    
    def _get_vk_friends(self, user_id: str):
        """Получение списка друзей"""
        if not user_id:
            return []
        
        url = f"https://vk.com/friends?id={user_id}&section=all"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            friends = []
            friend_blocks = soup.find_all('div', class_='friends_user_row')
            
            for friend_block in friend_blocks[:10]:  # Ограничиваемся 10 друзьями
                friend = {}
                
                # Имя и фамилия
                name_element = friend_block.find('a', class_='friends_field_title')
                if name_element:
                    friend['name'] = name_element.get_text(strip=True)
                
                # Ссылка на профиль
                if name_element and 'href' in name_element.attrs:
                    friend['link'] = f"https://vk.com{name_element['href']}"
                
                # Город
                city_element = friend_block.find('div', class_='friends_field')
                if city_element:
                    friend['city'] = city_element.get_text(strip=True)
                
                if friend:
                    friends.append(friend)
            
            return friends
        except:
            return []
    
    def _get_vk_groups(self, user_id: str):
        """Получение списка групп"""
        if not user_id:
            return []
        
        url = f"https://vk.com/groups?act=groups&id={user_id}"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            groups = []
            group_blocks = soup.find_all('div', class_='groups_row')
            
            for group_block in group_blocks[:5]:  # Ограничиваемся 5 группами
                group = {}
                
                # Название группы
                name_element = group_block.find('a', class_='groups_row_title')
                if name_element:
                    group['name'] = name_element.get_text(strip=True)
                
                # Ссылка на группу
                if name_element and 'href' in name_element.attrs:
                    group['link'] = f"https://vk.com{name_element['href']}"
                
                # Количество участников
                members_element = group_block.find('div', class_='groups_row_members')
                if members_element:
                    group['members'] = members_element.get_text(strip=True)
                
                if group:
                    groups.append(group)
            
            return groups
        except:
            return []
    
    def _format_vk_results(self, data: dict) -> str:
        """Форматирование результатов в читаемый вид"""
        output = []
        
        # Основная информация
        if user_info := data.get('user_info'):
            output.append("🔍 Основная информация о профиле")
            if name := user_info.get('name'):
                output.append(f"Имя: {name}")
            if status := user_info.get('status'):
                output.append(f"Статус: {status}")
            if followers := user_info.get('followers'):
                output.append(f"Подписчики: {followers}")
            
            # Дополнительная информация
            for key, value in user_info.items():
                if key not in ['name', 'status', 'followers', 'id']:
                    output.append(f"{key}: {value}")
            
            output.append("")
        
        # Посты
        if posts := data.get('posts'):
            output.append("📰 Последние посты пользователя")
            for i, post in enumerate(posts, 1):
                text = post.get('text', 'Текст отсутствует')
                date = post.get('date', 'Дата неизвестна')
                likes = post.get('likes', '0')
                reposts = post.get('reposts', '0')
                output.append(f"{i}. ({date}) {text}")
                output.append(f"   👍 {likes} ♻️ {reposts}")
            output.append("")
        
        # Друзья
        if friends := data.get('friends'):
            output.append("👥 Список друзей")
            for friend in friends:
                name = friend.get('name', 'Неизвестный')
                city = friend.get('city', 'Город неизвестен')
                link = friend.get('link', 'Ссылка отсутствует')
                output.append(f"- {name} ({city}) - {link}")
            output.append("")
        
        # Группы
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
            return {'success': False, 'error': 'Invalid IP'}
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get('status') == 'success':
                    return {'success': True, **d}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        return {'success': False, 'error': 'No data'}

    def lookup_hlr(self, number: str):
        url = "https://www.ipqualityscore.com/api/json/phone"
        params = {'key': 'Test', 'phone': number}
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if not data.get('success'):
                return {'success': False, 'error': data.get('message', 'HLR lookup failed')}
            return {'success': True, **data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

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
            return {'success': True, 'results': results}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_dorks(self, query: str):
        query = query.strip()
        if re.match(r'^(\+7|8)[\d\-\(\)\s]{10,}$', query):
            t = 'phone'
        elif re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', query):
            t = 'ip'
        elif re.match(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?$', query):
            t = 'name'
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
            t = 'email'
        else:
            t = 'general'
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
        return {'success': True, 'query_type': t, 'query': query, 'dorks': dorks_map.get(t, [])}

    def database_search(self, keyword: str):
        db_dir = 'data'
        if not os.path.exists(db_dir):
            return {'success': False, 'error': f"Folder '{db_dir}' does not exist"}
        files = [os.path.join(root, f) for root, _, files in os.walk(db_dir) for f in files]
        results_list = []
        stop = threading.Event()
        with concurrent.futures.ThreadPoolExecutor() as exe:
            fut = [exe.submit(self._search_file, fp, keyword, stop, results_list) for fp in files if not stop.is_set()]
            concurrent.futures.wait(fut)
        out = [f"File: {fp} | Line {ln}: {match}" for fp, ln, match in results_list]
        return {'success': True, 'keyword': keyword, 'matches_found': len(out), 'results': out}

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
            nv = requests.get(f"http://apilayer.net/api/validate?access_key={PHONE_API_KEY}&number={number}", timeout=7).json()
            if nv.get('valid'):
                results['numverify'] = nv
        except: pass
        try:
            ab = requests.get(f"https://phonevalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&phone={number}", timeout=5).json()
            if ab.get('valid'):
                results['abstract'] = ab
        except: pass
        try:
            hw = HttpWebNumber().lookup(number)
            if not hw.get('status_error'):
                results['htmlweb'] = hw
        except: pass
        return {'success': bool(results), 'number': number, 'results': results}

    def enhanced_ip_lookup(self, ip: str):
        results = {}
        try:
            ipapi = requests.get(f"http://ip-api.com/json/{ip}", timeout=7).json()
            if ipapi.get('status') == 'success':
                results['ipapi'] = ipapi
        except: pass
        try:
            ipinfo = requests.get(f"https://ipinfo.io/{ip}/json?token={IPINFO_API_KEY}", timeout=5).json()
            results['ipinfo'] = ipinfo
        except: pass
        try:
            shodan = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}", timeout=10).json()
            results['shodan'] = shodan
        except: pass
        return {'success': bool(results), 'ip': ip, 'results': results}

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
            return {'success': True, 'results': res}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _load_worker(self, ip, port, end, lock, cnt):
        ua = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"]
        async with aiohttp.ClientSession() as ses:
            while time.time() < end:
                try:
                    async with ses.get(f"http://{ip}:{port}", headers={'User-Agent': random.choice(ua)}, timeout=5) as resp:
                        pass
                except: pass
                async with lock: cnt[0] += 1
                await asyncio.sleep(0)

    async def run_load_test(self, target_ip, port, threads, duration):
        end = time.time() + duration
        lock, cnt = asyncio.Lock(), [0]
        tasks = [asyncio.create_task(self._load_worker(target_ip, port, end, lock, cnt)) for _ in range(threads)]
        await asyncio.gather(*tasks)
        return cnt[0]

    def leak_search(self, token: str, query: str):
        try:
            r = requests.post('https://leakosintapi.com/', json={'token': token, 'request': query, 'limit': 100000000000000000000000000, 'lang': 'en'}, timeout=15)
            r.raise_for_status()
            return {'success': True, 'results': r.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def mac_vendor_lookup(self, mac: str):
        mac = mac.lower().replace('-', ':').replace('.', ':')
        try:
            r = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
            if r.status_code == 200:
                return {'success': True, 'mac': mac, 'vendor': r.text}
        except: pass
        try:
            r = requests.get(f"https://macvendors.co/api/{mac}", timeout=5).json()
            if 'result' in r:
                return {'success': True, 'mac': mac, 'vendor': r['result'].get('company', 'Unknown')}
        except: pass
        return {'success': False, 'error': 'Vendor not found'}

    def depsearch_lookup(self, query: str):
        url = f'https://api.depsearch.digital/quest={query}?token={DEPSEARCH_TOKEN}&lang=ru'
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            if not data.get('results'):
                return {'success': False, 'error': 'No results'}
            return {'success': True, 'results': data['results']}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_qr_code(self, text: str):
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="white", back_color="#0a1a35")
            
            # Конвертируем изображение в base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {'success': True, 'qr_code': f"data:image/png;base64,{img_str}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_identity_card(self, name: str, age: str, address: str, phone: str, email: str):
        try:
            # Создаем изображение для ID карты
            img = Image.new('RGB', (400, 250), color='#0a1a35')
            d = ImageDraw.Draw(img)
            
            # Загружаем шрифт (используем стандартный, если нет другого)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Рисуем рамку
            d.rectangle([(10, 10), (390, 240)], outline='white', width=2)
            
            # Добавляем текст
            d.text((20, 20), "IDENTITY CARD", font=font, fill='white')
            d.text((20, 50), f"Name: {name}", font=font, fill='white')
            d.text((20, 80), f"Age: {age}", font=font, fill='white')
            d.text((20, 110), f"Address: {address}", font=font, fill='white')
            d.text((20, 140), f"Phone: {phone}", font=font, fill='white')
            d.text((20, 170), f"Email: {email}", font=font, fill='white')
            
            # Добавляем дату
            from datetime import datetime
            date_str = datetime.now().strftime("%Y-%m-%d")
            d.text((20, 200), f"Issued: {date_str}", font=font, fill='white')
            
            # Конвертируем изображение в base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {'success': True, 'id_card': f"data:image/png;base64,{img_str}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _random_ua(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"

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

api = Api()

html = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>OSINT Toolkit</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a1a35 0%, #1a3a6c 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 10px rgba(0, 242, 254, 0.3);
        }
        .header p {
            color: #a0d2ff;
            font-size: 1.1em;
        }
        .tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }
        .tab-button {
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        .tab-button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .tab-button.active {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            color: #0a1a35;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
        }
        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .tab-content.active {
            display: block;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #4facfe;
        }
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 12px 15px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .input-group input:focus, .input-group textarea:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.5);
        }
        button {
            padding: 12px 25px;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            border: none;
            border-radius: 8px;
            color: #0a1a35;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            border-left: 4px solid #4facfe;
            max-height: 400px;
            overflow-y: auto;
        }
        .result div[contenteditable="true"] {
            white-space: pre-wrap;
            word-break: break-word;
            color: #e1e9ff;
            font-family: 'Consolas', monospace;
            padding: 10px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 4px;
            min-height: 100px;
            max-height: 400px;
            overflow-y: auto;
            outline: none;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .loading-spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 3px solid #4facfe;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
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
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        .card h3 {
            color: #4facfe;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

  .starfall {
            position: absolute;
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
            0% {
                transform: translate(100vw, -100px) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translate(-100px, 100vh) rotate(360deg);
                opacity: 0;
            }
        }

        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            color: #a0d2ff;
            font-size: 0.9em;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #a0d2ff;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .tabs { flex-direction: column; }
            .tab-button { width: 100%; }
            .grid { grid-template-columns: 1fr; }
        }
        .tooltip {
            position: relative;
            display: inline-block;
            margin-left: 5px;
            cursor: help;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: rgba(10, 26, 53, 0.9);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        .qr-code, .id-card {
            display: block;
            margin: 20px auto;
            max-width: 200px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
    </style>
</head>
<body>

 <div class="starfall" id="starfall"></div>

    <div class="container">
        <div class="header">
            <h1>💧 Arasaka Project</h1>
            <p>arasaka - наблюдение это исскуство..</p>
        </div>

        <div class="tabs">
            <button class="tab-button active" onclick="showTab('username-tab')">👤 Username</button>
            <button class="tab-button" onclick="showTab('email-tab')">📧 Email</button>
            <button class="tab-button" onclick="showTab('phone-tab')">📞 Phone</button>
            <button class="tab-button" onclick="showTab('ip-tab')">🌐 IP</button>
            <button class="tab-button" onclick="showTab('vk-tab')">🔍 VK OSINT</button>
            <button class="tab-button" onclick="showTab('domain-tab')">🌍 Domain</button>
            <button class="tab-button" onclick="showTab('dork-tab')">🔎 Dorks</button>
            <button class="tab-button" onclick="showTab('database-tab')">💾 Database</button>
            <button class="tab-button" onclick="showTab('tools-tab')">🛠️ Tools</button>
        </div>

        <div id="username-tab" class="tab-content active">
            <div class="input-group">
                <label for="username">Username:</label>
                <input type="text" id="username" placeholder="Enter username to search across social networks">
            </div>
            <button onclick="searchUsername()">Search Username</button>
            <div class="loading" id="username-loading">
                <div class="loading-spinner"></div>
                <p>Searching across social networks...</p>
            </div>
            <div class="result" id="username-result"></div>
        </div>

        <div id="email-tab" class="tab-content">
            <div class="input-group">
                <label for="email">Email Address:</label>
                <input type="email" id="email" placeholder="Enter email to check for breaches">
            </div>
            <button onclick="searchEmail()">Check Email</button>
            <div class="loading" id="email-loading">
                <div class="loading-spinner"></div>
                <p>Checking email in breach databases...</p>
            </div>
            <div class="result" id="email-result"></div>
        </div>

        <div id="phone-tab" class="tab-content">
            <div class="input-group">
                <label for="phone">Phone Number:</label>
                <input type="text" id="phone" placeholder="Enter phone number (e.g. +79123456789)">
            </div>
            <button onclick="lookupPhone()">Lookup Phone</button>
            <div class="loading" id="phone-loading">
                <div class="loading-spinner"></div>
                <p>Looking up phone number information...</p>
            </div>
            <div class="result" id="phone-result"></div>
        </div>

        <div id="ip-tab" class="tab-content">
            <div class="input-group">
                <label for="ip">IP Address:</label>
                <input type="text" id="ip" placeholder="Enter IP address for geolocation and info">
            </div>
            <button onclick="lookupIP()">Lookup IP</button>
            <div class="loading" id="ip-loading">
                <div class="loading-spinner"></div>
                <p>Looking up IP address information...</p>
            </div>
            <div class="result" id="ip-result"></div>
        </div>

        <div id="vk-tab" class="tab-content">
            <div class="input-group">
                <label for="vk-query">VK Username or ID:</label>
                <input type="text" id="vk-query" placeholder="Enter VK username or ID for OSINT analysis">
            </div>
            <button onclick="vkOsint()">Analyze VK Profile</button>
            <div class="loading" id="vk-loading">
                <div class="loading-spinner"></div>
                <p>Analyzing VK profile...</p>
            </div>
            <div class="result" id="vk-result"></div>
        </div>

        <div id="domain-tab" class="tab-content">
            <div class="input-group">
                <label for="domain">Domain Name:</label>
                <input type="text" id="domain" placeholder="Enter domain for WHOIS lookup">
            </div>
            <button onclick="domainWhois()">WHOIS Lookup</button>
            <div class="loading" id="domain-loading">
                <div class="loading-spinner"></div>
                <p>Performing WHOIS lookup...</p>
            </div>
            <div class="result" id="domain-result"></div>
        </div>

        <div id="dork-tab" class="tab-content">
            <div class="input-group">
                <label for="dork-query">Search Query:</label>
                <input type="text" id="dork-query" placeholder="Enter phone, email, name, IP or general query">
            </div>
            <button onclick="generateDorks()">Generate Dorks</button>
            <div class="loading" id="dork-loading">
                <div class="loading-spinner"></div>
                <p>Generating Google dorks...</p>
            </div>
            <div class="result" id="dork-result"></div>
        </div>

        <div id="database-tab" class="tab-content">
            <div class="input-group">
                <label for="db-keyword">Keyword Search:</label>
                <input type="text" id="db-keyword" placeholder="Enter keyword to search in local database">
            </div>
            <button onclick="searchDatabase()">Search Database</button>
            <div class="loading" id="db-loading">
                <div class="loading-spinner"></div>
                <p>Searching in local database...</p>
            </div>
            <div class="result" id="db-result"></div>
        </div>

        <div id="tools-tab" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h3>QR Code Generator</h3>
                    <div class="input-group">
                        <label for="qr-text">Text/URL:</label>
                        <input type="text" id="qr-text" placeholder="Enter text or URL for QR code">
                    </div>
                    <button onclick="generateQR()">Generate QR Code</button>
                    <div id="qr-result"></div>
                </div>

                <div class="card">
                    <h3>Fake Identity Generator</h3>
                    <div class="input-group">
                        <label for="id-name">Name:</label>
                        <input type="text" id="id-name" placeholder="Full Name">
                    </div>
                    <div class="input-group">
                        <label for="id-age">Age:</label>
                        <input type="text" id="id-age" placeholder="Age">
                    </div>
                    <div class="input-group">
                        <label for="id-address">Address:</label>
                        <input type="text" id="id-address" placeholder="Address">
                    </div>
                    <div class="input-group">
                        <label for="id-phone">Phone:</label>
                        <input type="text" id="id-phone" placeholder="Phone">
                    </div>
                    <div class="input-group">
                        <label for="id-email">Email:</label>
                        <input type="text" id="id-email" placeholder="Email">
                    </div>
                    <button onclick="generateID()">Generate ID Card</button>
                    <div id="id-result"></div>
                </div>

                <div class="card">
                    <h3>MAC Address Lookup</h3>
                    <div class="input-group">
                        <label for="mac-address">MAC Address:</label>
                        <input type="text" id="mac-address" placeholder="Enter MAC address (e.g. 00:1A:2B:3C:4D:5E)">
                    </div>
                    <button onclick="lookupMAC()">Lookup Vendor</button>
                    <div class="result" id="mac-result"></div>
                </div>

                <div class="card">
                    <h3>Network Tools</h3>
                    <div class="input-group">
                        <label for="load-target">Target IP:</label>
                        <input type="text" id="load-target" placeholder="Target IP address">
                    </div>
                    <div class="input-group">
                        <label for="load-port">Port:</label>
                        <input type="number" id="load-port" placeholder="Port" value="80">
                    </div>
                    <div class="input-group">
                        <label for="load-threads">Threads:</label>
                        <input type="number" id="load-threads" placeholder="Threads" value="10">
                    </div>
                    <div class="input-group">
                        <label for="load-duration">Duration (sec):</label>
                        <input type="number" id="load-duration" placeholder="Duration" value="10">
                    </div>
                    <button onclick="runLoadTest()">Run Load Test</button>
                    <div class="result" id="load-result"></div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>
        <img src="https://img.icons8.com/fluency/24/000000/comet.png" alt="Comet Logo" style="vertical-align: middle; width: 20px; height: 20px;">
        OSINT Space Toolkit v2.0 | Created with advanced OSINT capabilities
    </p>
</div>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

         const starfall = document.getElementById('starfall');
        for (let i = 0; i < 180; i++) {
            const star = document.createElement('span');
            /* случайный старт за пределами экрана по всему периметру */
            star.style.left = (Math.random() * 200 - 50) + '%';
            star.style.top  = (Math.random() * 200 - 50) + '%';
            star.style.setProperty('--delay', Math.random() * 12 + 's');
            star.style.setProperty('--duration', (6 + Math.random() * 8) + 's');
            const size = 1 + Math.random() * 3; /* 1–4 px */
            star.style.width  = size + 'px';
            star.style.height = size + 'px';
            starfall.appendChild(star);
        }

        function showLoading(id) {
            document.getElementById(id).style.display = 'block';
        }

        function hideLoading(id) {
            document.getElementById(id).style.display = 'none';
        }

        function displayResult(id, data) {
            const resultDiv = document.getElementById(id);
            if (data.success) {
                resultDiv.innerHTML = `<div contenteditable="true">${JSON.stringify(data, null, 2)}</div>`;
            } else {
                resultDiv.innerHTML = `<div contenteditable="true" style="color: #ff6b6b;">Error: ${data.error || 'Unknown error'}</div>`;
            }
        }

        async function searchUsername() {
            const username = document.getElementById('username').value;
            if (!username) return alert('Please enter a username');
            
            showLoading('username-loading');
            try {
                const result = await pywebview.api.search_username(username);
                displayResult('username-result', result);
            } catch (error) {
                displayResult('username-result', {success: false, error: error.message});
            }
            hideLoading('username-loading');
        }

        async function searchEmail() {
            const email = document.getElementById('email').value;
            if (!email) return alert('Please enter an email');
            
            showLoading('email-loading');
            try {
                const result = await pywebview.api.email_search(email);
                displayResult('email-result', result);
            } catch (error) {
                displayResult('email-result', {success: false, error: error.message});
            }
            hideLoading('email-loading');
        }

        async function lookupPhone() {
            const phone = document.getElementById('phone').value;
            if (!phone) return alert('Please enter a phone number');
            
            showLoading('phone-loading');
            try {
                const result = await pywebview.api.phone_lookup(phone);
                displayResult('phone-result', result);
            } catch (error) {
                displayResult('phone-result', {success: false, error: error.message});
            }
            hideLoading('phone-loading');
        }

        async function lookupIP() {
            const ip = document.getElementById('ip').value;
            if (!ip) return alert('Please enter an IP address');
            
            showLoading('ip-loading');
            try {
                const result = await pywebview.api.enhanced_ip_lookup(ip);
                displayResult('ip-result', result);
            } catch (error) {
                displayResult('ip-result', {success: false, error: error.message});
            }
            hideLoading('ip-loading');
        }

        async function vkOsint() {
            const query = document.getElementById('vk-query').value;
            if (!query) return alert('Please enter a VK username or ID');
            
            showLoading('vk-loading');
            try {
                const result = await pywebview.api.vk_osint(query);
                displayResult('vk-result', result);
            } catch (error) {
                displayResult('vk-result', {success: false, error: error.message});
            }
            hideLoading('vk-loading');
        }

        async function domainWhois() {
            const domain = document.getElementById('domain').value;
            if (!domain) return alert('Please enter a domain name');
            
            showLoading('domain-loading');
            try {
                const result = await pywebview.api.domain_whois(domain);
                displayResult('domain-result', result);
            } catch (error) {
                displayResult('domain-result', {success: false, error: error.message});
            }
            hideLoading('domain-loading');
        }

        async function generateDorks() {
            const query = document.getElementById('dork-query').value;
            if (!query) return alert('Please enter a search query');
            
            showLoading('dork-loading');
            try {
                const result = await pywebview.api.generate_dorks(query);
                displayResult('dork-result', result);
            } catch (error) {
                displayResult('dork-result', {success: false, error: error.message});
            }
            hideLoading('dork-loading');
        }

        async function searchDatabase() {
            const keyword = document.getElementById('db-keyword').value;
            if (!keyword) return alert('Please enter a keyword');
            
            showLoading('db-loading');
            try {
                const result = await pywebview.api.database_search(keyword);
                displayResult('db-result', result);
            } catch (error) {
                displayResult('db-result', {success: false, error: error.message});
            }
            hideLoading('db-loading');
        }

        async function generateQR() {
            const text = document.getElementById('qr-text').value;
            if (!text) return alert('Please enter text or URL');
            
            try {
                const result = await pywebview.api.generate_qr_code(text);
                if (result.success) {
                    document.getElementById('qr-result').innerHTML = `
                        <img src="${result.qr_code}" alt="QR Code" class="qr-code">
                        <p style="text-align: center;">QR Code generated successfully!</p>
                        <div contenteditable="true" style="margin-top: 10px; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);">
                            QR Code for: ${text}
                        </div>
                    `;
                } else {
                    document.getElementById('qr-result').innerHTML = `<p style="color: #ff6b6b;">Error: ${result.error}</p>`;
                }
            } catch (error) {
                document.getElementById('qr-result').innerHTML = `<p style="color: #ff6b6b;">Error: ${error.message}</p>`;
            }
        }

        async function generateID() {
            const name = document.getElementById('id-name').value;
            const age = document.getElementById('id-age').value;
            const address = document.getElementById('id-address').value;
            const phone = document.getElementById('id-phone').value;
            const email = document.getElementById('id-email').value;
            
            if (!name || !age || !address || !phone || !email) {
                return alert('Please fill all identity fields');
            }
            
            try {
                const result = await pywebview.api.generate_identity_card(name, age, address, phone, email);
                if (result.success) {
                    document.getElementById('id-result').innerHTML = `
                        <img src="${result.id_card}" alt="ID Card" class="id-card">
                        <p style="text-align: center;">ID Card generated successfully!</p>
                        <div contenteditable="true" style="margin-top: 10px; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);">
                            Name: ${name}
                            Age: ${age}
                            Address: ${address}
                            Phone: ${phone}
                            Email: ${email}
                        </div>
                    `;
                } else {
                    document.getElementById('id-result').innerHTML = `<p style="color: #ff6b6b;">Error: ${result.error}</p>`;
                }
            } catch (error) {
                document.getElementById('id-result').innerHTML = `<p style="color: #ff6b6b;">Error: ${error.message}</p>`;
            }
        }

        async function lookupMAC() {
            const mac = document.getElementById('mac-address').value;
            if (!mac) return alert('Please enter a MAC address');
            
            try {
                const result = await pywebview.api.mac_vendor_lookup(mac);
                displayResult('mac-result', result);
            } catch (error) {
                displayResult('mac-result', {success: false, error: error.message});
            }
        }

        async function runLoadTest() {
            const target = document.getElementById('load-target').value;
            const port = document.getElementById('load-port').value;
            const threads = document.getElementById('load-threads').value;
            const duration = document.getElementById('load-duration').value;
            
            if (!target || !port || !threads || !duration) {
                return alert('Please fill all load test fields');
            }
            
            try {
                const result = await pywebview.api.run_load_test(target, parseInt(port), parseInt(threads), parseInt(duration));
                document.getElementById('load-result').innerHTML = `
                    <div contenteditable="true">Load test completed! Requests sent: ${result}</div>
                `;
            } catch (error) {
                document.getElementById('load-result').innerHTML = `<div contenteditable="true" style="color: #ff6b6b;">Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
'''

def start_gui():
    window = webview.create_window(
        'OSINT Space Toolkit',
        html=html,
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
        background_color='#0a1a35'
    )
    webview.start(debug=True)

if __name__ == '__main__':
    start_gui()