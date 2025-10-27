# download media files
from tqdm import tqdm
import requests
import os

# transcribe 
from faster_whisper import WhisperModel
import re


# make a list of podcast still needs to be downloaded
import json
# import os
import re

from pathlib import Path
path = Path('../../../spotify-project/ingest-data/media-files')

def make_queue(rss_path: str, media_directory:str):
    """ Returns a list of episodes that still needs to be downloaded."""
    with open(rss_path, 'r', encoding='utf-8') as f_in:
        rss_feed = json.load(f_in)
    
    episodes = [ep['ep_name'] for ep in rss_feed]
    downloaded_list = [re.split(r'\.', t)[0] for t in set(os.listdir(media_directory))]
    to_download = [ep for ep in episodes if ep not in downloaded_list]


    download_queue_dict = []
    for p_to_download in set(to_download):
        for p in rss_feed:
            ep_name_rss = p['ep_name'] 
            if p_to_download == ep_name_rss:
                download_queue_dict.append(
                    {'name_of_podcast': p['name_of_podcast'],
                     'categories': p['categories'],
                     'language': p['language'],
                    'ep_name': ep_name_rss,
                    'duration': p['duration'],
                    'media_url': p['media_url']}
                )
    return download_queue_dict

# download one file
def download_media_file(media_file:str, media_files_directory=path):
    os.makedirs(media_files_directory, exist_ok=True) 
    
    # for t in test_sample:
    media_url = media_file['media_url']
    filename = f"{path}/{media_file['ep_name']}.mp3"
    audio_path = f"{path}/{media_files_directory}/{filename}"
    with requests.get(media_url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))

        with open(audio_path, 'wb') as f_out, tqdm(total=total, unit='B', unit_scale=True, desc=filename) as bar:
            for chunk in r.iter_content(1024 * 1024):
                f_out.write(chunk)
                bar.update(len(chunk))
    
    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
        print(f"Successful download: {filename}.")
    else:
        print(f"Download not successful: {filename}")

def format_time(seconds:float):
    sec = int(seconds)
    hour, remainder = divmod(sec, 3600)
    min, sec = divmod(remainder, 60)
    return f"{hour:02d}:{min:02d}:{sec:02d}"


def transcribe_audio_file(audiofile:str, model_size_or_path='tiny', device='cpu', compute_type='int8'):
    
    model = WhisperModel(model_size_or_path=model_size_or_path, device=device, compute_type=compute_type)
    segments, info = model.transcribe(audiofile, vad_filter=True)

    name_of_episode_extract = re.search(r'media-files/(.*?).mp3', audiofile)
    name_of_episode = name_of_episode_extract.group(1)

    with open(f"{path}/{name_of_episode}.txt", 'w', encoding='utf-8') as f_out, \
    tqdm(total = float(info.duration), unit='s', desc=f"Transcribing: {name_of_episode}") as bar:
        for s in segments:
            line = f"({format_time(s.start)}) {s.text.strip()}"
            f_out.write(line + '\n')
            f_out.flush() # ensures that data is physically written to disk and not held in memory

            bar.n = min(s.end, info.duration)
            bar.refresh()
        bar.n = bar.total
        bar.refresh()

# process multiple files
def ingest_data(rss_path: str, media_directory:str, num_of_files:int):
    download_queue = make_queue(rss_path, media_directory)

    for f in download_queue[:num_of_files]:
        download_media_file(f)

        audio_file_path = f"{path}/{f['ep_name']}.mp3"
        transcribe_audio_file(audio_file_path)

        transcript_path = f"{path}/{f['ep_name']}.txt"
        if os.path.exists(transcript_path) and os.path.getsize(transcript_path) > 0:
            os.remove(audio_file_path)
            print(f'Deleted: {audio_file_path}')
            

