import requests
from bs4 import BeautifulSoup
import os
import yaml
from datetime import datetime

class NewsOnAIR:
    def __init__(self, language,config_file_path):
        self.config_file_path = config_file_path
        self.config = self.load_config()
        self.language = language
        self.base_url = "https://newsonair.gov.in/"
        if self.language.lower() not in ['hindi', 'english']:
            raise ValueError
    
    def load_config(self):
        try:
            with open(self.config_file_path,'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            d = {}
            return d

    def save_news(self, audio_link, title):
        response = requests.get(audio_link)
        temp_dir = "/tmp/Audio"  
        os.makedirs(temp_dir, exist_ok=True)
    
        if response.status_code == 200:
            temp_file_path = os.path.join(temp_dir, title)
            with open(temp_file_path, 'wb') as audioFile:
                audioFile.write(response.content)
            return temp_file_path
        else:
            return None
        
    def send_audio_message(self,audio_file_path,chat_id,caption):
        url = f"https://api.telegram.org/bot{self.config['TELEGRAM_BOT_TOKEN']}/sendAudio"
        files = {'audio': open(audio_file_path, 'rb')}
        data = {'chat_id': chat_id, 'caption': caption}
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Audio message sent successfully!")
        else:
            print(f"Failed to send audio message. Status code: {response.status_code}")
            print(response.text)

    def get_news(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.content, features='html.parser')
        try:
            newsboxes = soup.select('.accordion-body')
            nb = newsboxes[0] if self.language.lower() == 'english' else newsboxes[1]
            if self.language.lower() == "hindi":
                nb = newsboxes[1]
            elif self.language.lower() == "english":
                nb = newsboxes[0]
            all_audio_elements = nb.find_all('audio')
            file_paths = []
            for i, audio_element in enumerate(all_audio_elements):
                audio_link = audio_element.get('src')
                filename = audio_link.split('/')[-1]
                if not filename.endswith('.mp3'):
                    filename = filename + ".mp3"
                saved_path = self.save_news(title=filename, audio_link=audio_link)
                if saved_path:
                    file_paths.append(saved_path)
                    print(f"Saved {filename}")
            if file_paths:
                for file in file_paths:
                    chat_ids = self.config['TELEGRAM_CHAT_IDS'].values()
                    try:
                        caption=file.split('/')[-1].split(".")[0]
                    except Exception as e:
                        caption=file.split('/')[-1]
                    for chat_id in chat_ids:
                        self.send_audio_message(audio_file_path=file,chat_id=chat_id,caption=caption)
                        print(f"Sent to {chat_id}")
                for file in file_paths:
                    os.remove(file)
            else:
                print("No audio files to send")
        except Exception as e:
            print(f"An Error Occurred: {str(e)}")
            return None


def lambda_handler(event,context):
    ni = NewsOnAIR(language='English',config_file_path="config.yaml")
    ni.get_news()