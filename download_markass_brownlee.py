import json
import requests
import os
from PIL import Image
import pillow_avif
from io import BytesIO
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor as TPE, as_completed as AC


def fetch_image_repo(url: str) -> json:
    response = requests.get(url)
    return response.json()

def find_picture_urls(data: json) -> list[str]:
    urls = []
    if(isinstance(data, dict)):
        for key, val in data.items():
            urls.extend(find_picture_urls(val))
    elif(isinstance(data, str)) and data.startswith('https://'):
        urls.append(data)
    
    return urls

def download_image(url: str, download_location: str, curr_index: int) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))

        if(image.width < 200 or image.height < 200):
            print(f'Skipping retarded shit: {url}')
            return None
        
        image_file_name = f'image_{curr_index + 1}.png'
        image_file_path = os.path.join(download_location, image_file_name)
        image.save(image_file_path, format='PNG')
        print(f'Downloading... {image_file_name}')
        return image_file_name

    except requests.exceptions.RequestException as ex:
        print('Request problem: {ex}')

    except Exception as ex:
        print(f'Shit blew up, not good {ex}')

def download_image_multithread(urls: list[str], download_location: str) -> None:
    with TPE(max_workers=5) as executor:
        futures = {executor.submit(download_image, url, download_location, index): url for index, url in enumerate(urls)}
        for f in AC(futures):
            f.result()

def main():
    JSON_REPO = "https://storage.googleapis.com/panels-api/data/20240916/media-1a-i-p~s"
    DOWNLOAD_LOCATION = "D:/Downloads/Images"
    
    if(not os.path.exists(DOWNLOAD_LOCATION)):
        os.mkdir(DOWNLOAD_LOCATION)
    
    json_data = fetch_image_repo(JSON_REPO)
    image_urls = find_picture_urls(json_data)

    download_image_multithread(image_urls, DOWNLOAD_LOCATION)
    

if __name__ == '__main__':
    main()
