import concurrent.futures
import os
import sys
import uuid
import time
from tqdm import tqdm  # Импортируем tqdm для создания прогресс-бара
import requests


def download_file(file_info, dir_name):
    file_path = file_info['path']
    prefix = 'https://2ch.hk'
    with requests.get(prefix + file_path) as r:
        with open(os.path.join(dir_name, file_info['name']), 'wb') as f:
            f.write(r.content)


def parse(url, dir_name=None, save_videos=False):
    start_time = time.time()  # Запоминаем время начала выполнения
    api_content_as_json = url[0:-4] + 'json'

    with requests.get(api_content_as_json) as response:
        if dir_name is None:
            dir_name = str(uuid.uuid4())

        response_json = response.json()
        posts = response_json['threads'][0]['posts']
        image_extensions = ['jpg', 'jpeg', 'png', 'bmp']

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for post in posts:
                if post['files'] is not None:
                    files = post['files']
                    for file in files:
                        file_extension = file['name'].split('.')[-1]
                        if not save_videos:
                            if file_extension in image_extensions:
                                futures.append(executor.submit(download_file, file, dir_name))
                                continue
                        if save_videos:
                            futures.append(executor.submit(download_file, file, dir_name))
                            continue

            # Используем tqdm для создания прогресс-бара
            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Загрузка"):
                pass

    end_time = time.time()  # Запоминаем время завершения выполнения
    elapsed_time = end_time - start_time  # Вычисляем затраченное время
    print(f"Затраченное время: {elapsed_time:.2f} секунд")


if __name__ == '__main__':
    try:
        url = sys.argv[1]
        directory_name = sys.argv[2] if len(sys.argv) > 2 else None
        is_need_to_save_videos = True if len(sys.argv) > 3 and sys.argv[3].lower() == 'y' else False
        parse(url, directory_name, is_need_to_save_videos)
    except IndexError:
        print(f'Usage: python main.py <url> [dir_name] [save_videos=y]')
