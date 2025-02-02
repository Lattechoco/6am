import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytubefix.cli import on_progress

from moviepy import *
import moviepy.audio.AudioClip as audio
from moviepy.editor import AudioFileClip

from urllib.parse import quote
import urllib
import re

import subprocess
import os
from tqdm import tqdm
from tqdm import trange
import time

cid = 'f0c08080505c44a9ad61fd3b1dc36242'
secret = '6075359d9ce54847bdcdeff919c22667'

#Authentication#
client_credentials_mgmt = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_mgmt)


def download_process():
    #for file in os.scandir('output'):
    #    os.remove(file.path)
    #print('Initiating..')
    track_list = get_playlist('https://open.spotify.com/playlist/2aOVUWcMjSSF6SzjWDxnIO')

    #search_result_list = find_youtube(track_list)

    #download_yt(search_result_list)
    
    check_update(track_list)
    
def get_playlist(playlist_url):
    target_playlist = playlist_url
    track_list = [] # list of songs in playlist

    items = sp.playlist_tracks(target_playlist)["items"]
    for x in tqdm(items, desc='Getting playlist info'):
        playlist_URI = target_playlist.split("/")[-1].split("?")[0]  

    tracks = sp.playlist_tracks(playlist_URI)["items"]
    for track in tqdm(tracks,desc='Listing track names'):
        # get track name
        track_name = track["track"]["name"]

        # get main artist
        artist_uri = track["track"]["artists"][0]["uri"]
        artist_info = sp.artist(artist_uri)

        song_info = '%s-%s'%(artist_info['name'], track_name)
        track_list.extend([song_info])

    return track_list

def find_youtube(track_list):
    search_results_list = []

    for i in trange(len(track_list), desc='Find tracks on Youtube'):
        query = track_list[i]
        #print(query)
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            #print("search url =", search_url)
            response = urllib.request.urlopen(search_url)
            search_results = re.findall(r"watch\?v=(\S{11})", response.read().decode('utf-8'))
            #print("search_results =", search_results)
            search_results_list.append(search_results)

        except Exception as e:
            raise ValueError(f"Failed to find YouTube video: {e}")
    
    return search_results_list
    

def download_yt(search_result_list):
    for i in trange(len(search_result_list), desc='Downloading tracks'):
        link = f"https://www.youtube.com/watch?v={search_result_list[i][0]}"

        try:
            yt = YouTube(link, on_progress_callback = on_progress)
            
            yt.title = re.sub(r'[\\/:*?"<>|]', "", yt.title)  # Sanitize file name
            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            ys = yt.streams.filter(only_audio=True).first()
            downloaded_file = ys.download(output_path=output_dir)
            audio_file = os.path.splitext(downloaded_file)[0] + ".mp3"
            
            with AudioFileClip(downloaded_file) as audio_clip:
                audio_clip.write_audiofile(audio_file, logger=None)

            os.remove(downloaded_file)
        
        except Exception as e:
            raise ValueError(f"Failed to download YouTube video: {e}")
            return 1
        
def check_update(old_track_list):
    while True:
        new_track_list = get_playlist('https://open.spotify.com/playlist/2aOVUWcMjSSF6SzjWDxnIO')   
        if old_track_list == new_track_list:
            print("There is no change on playlist..")
        else:
            print("There is update on playlist")
            add_track_list = list(set(new_track_list)-set(old_track_list))
            delete_track_list = list(set(old_track_list)-set(new_track_list))
            add_process(add_track_list)
            delete_process(delete_track_list)
        time.sleep(10)

def add_process(add_track_list):
    # Add new song
    search_result_list = find_youtube(add_track_list)
    download_yt(search_result_list)

    
    track_list = get_playlist('https://open.spotify.com/playlist/2aOVUWcMjSSF6SzjWDxnIO')
    check_update(track_list)
     
def delete_process(delete_track_list):
    #delete unliked song
    for i in trange(len(delete_track_list), desc='Finding name to delete'):
        track_to_delete = find_youtube(delete_track_list)
        link = f"https://www.youtube.com/watch?v={track_to_delete[i][0]}"
        try:
            yt = YouTube(link, on_progress_callback = on_progress)
            yt.title = re.sub(r'[\\/:*?"<>|]', "", yt.title)  # Sanitize file name
            
            output_dir = "output"
            ys = yt.streams.filter(only_audio=True).first()
            downloaded_file = ys.download(output_path=output_dir)
            audio_file = os.path.splitext(downloaded_file)[0] + ".mp3"
            os.remove(downloaded_file)
            print('!!!!!!!!!', audio_file, '!!!!!!!!!')
            
        except Exception as e:
            raise ValueError(f"Failed to download YouTube video: {e}")
            return 1
        
if __name__ == "__main__":
    download_process() 
