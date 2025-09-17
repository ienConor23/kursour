import requests
import json
import time
import subprocess
import tempfile
import os
from bs4 import BeautifulSoup

BANNER = r"""
 █████╗ ██╗  ██╗██╗██╗     ███████╗
██╔══██╗██║ ██╔╝██║██║     ██╔════╝
███████║█████╔╝ ██║██║     █████╗
██╔══██║██╔═██╗ ██║██║     ██╔══╝
██║  ██║██║  ██╗██║███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝
  Fast lookup & image preview tool
"""

print(BANNER)

def search_faces(image_path):
    url = "https://similarfaces.me/api/search-faces"
    
    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка запроса: {response.status_code}")
            return None

def parse_vk_profile(vk_id):
    try:
        url = f"https://vk.com/id{vk_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        profile_info = {}
        
        title = soup.find('title')
        if title:
            profile_info['name'] = title.text.split('|')[0].strip()
        
        city_elem = soup.find('div', class_='pp_info')
        if not city_elem:
            city_elem = soup.find('div', class_='profile_info_row')
        if city_elem:
            profile_info['city'] = city_elem.text.strip()
        
        return profile_info
    except Exception as e:
        print(f"Ошибка парсинга VK: {e}")
        return None

def display_image_with_viu(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            try:
                result = subprocess.run(['viu', '-w', '87', tmp_file_path], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print("Не удалось отобразить изображение через viu")
            except subprocess.TimeoutExpired:
                print("Таймаут отображения изображения")
            except FileNotFoundError:
                print("viu не установлен. Установите: cargo install viu")
            finally:
                os.unlink(tmp_file_path)
        else:
            print("Не удалось загрузить изображение")
    except Exception as e:
        print(f"Ошибка отображения изображения: {e}")

def display_person_info(person, index):
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТ #{index}")
    print(f"{'='*60}")
    print(f"👤 Имя: {person['name']}")
    print(f"📊 Совпадение: {person['similarity_rate']}%")
    print(f"🏙️ Город: {person['city']}")
    print(f"🔗 VK ID: {person['vk_id']}")
    print(f"🌐 Профиль: https://vk.com/id{person['vk_id']}")
    print(f"🖼️ Фото: {person['image_url']}")
    
    print("\n📸 Изображение:")
    display_image_with_viu(person['image_url'])
    
    print("\n📋 Информация с VK:")
    vk_info = parse_vk_profile(person['vk_id'])
    if vk_info:
        for key, value in vk_info.items():
            print(f"   {key}: {value}")
    else:
        print("   Не удалось получить дополнительную информацию")

def main():
    image_path = input("Введите путь к изображению: ")
    
    print("\n🔍 Поиск похожих лиц...")
    print("⏳ Ожидание 20-25 секунд...")
    start_time = time.time()
    
    result = search_faces(image_path)
    
    if result and result.get('ok') and result.get('results'):
        end_time = time.time()
        search_duration = end_time - start_time
        
        print(f"\n✅ Поиск завершен за {search_duration:.2f} секунд")
        print(f"📈 Найдено результатов: {len(result['results'])}")
        
        for i, person in enumerate(result['results'], 1):
            display_person_info(person, i)
            
            if i < len(result['results']):
                input("\nНажмите Enter для просмотра следующего результата...")
    
    else:
        print("❌ Не удалось получить результаты поиска")

if __name__ == "__main__":
    main()