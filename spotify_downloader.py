import concurrent.futures
import datetime
import os
import re
import unicodedata
import urllib.request

import moviepy.editor as mp
import spotipy
import youtube_dl
from spotipy.oauth2 import SpotifyOAuth

from schema import DatabaseHandler, Downloads


class SpotifyDownloader:
    def __init__(self):
        pass
        # self.export_credentials()
        self.database_handler = DatabaseHandler()
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))
        self.download_path = '/Users/mountain/Desktop/AltWorks/SpotifyDownloader/Files/'
        with youtube_dl.YoutubeDL({'outtmpl': 'Files/%(title)s.%(ext)s', 'format': 'bestaudio/best',
                                   'postprocessors': [{
                                       'key': 'FFmpegExtractAudio',
                                       'preferredcodec': 'mp3',
                                       'preferredquality': '192'}]}) as downloader:
            self.youtube_download = downloader

    @staticmethod
    def export_credentials():
        """
        """

    def get_all_downloaded_filenames(self):
        return os.listdir(self.download_path)

    def convert_mp4_to_mp3(self, video_file):
        mp.VideoFileClip(self.download_path + video_file).audio.write_audiofile(video_file.replace("mp4", "mp3"))

    @staticmethod
    def search_for_youtube_url(search_terms):
        print("Search Terms", search_terms)
        try:
            url = "https://www.youtube.com/watch?v=" + re.findall(r"watch\?v=(\S{11})", urllib.request.urlopen(
                "https://www.youtube.com/results?search_query=" + search_terms).read().decode())[0]
            print("URL FOUND FOR", search_terms.replace("-", " "))
            return url
        except Exception:
            print("URL NOT FOUND FOR", search_terms.replace("-", " "))
            return None

    def convert_all_mp4s_to_mp3(self):
        for file in self.get_all_downloaded_filenames():
            if "mp4" in file:
                self.convert_mp4_to_mp3(file)
                os.remove(self.download_path + file)
                os.rename(self.download_path.replace("Files/", "") + file.replace("mp4", "mp3"),
                          self.download_path.replace("Files", "Tracks") + file.replace("mp4", "mp3"))

    @staticmethod
    def time_desired(date):
        if datetime.datetime.strptime(date, '%Y-%m-%d') > datetime.datetime.today() - datetime.timedelta(days=365):
            return True
        return False

    def get_starred_tracks(self, num_tracks=500):
        track_data = []
        limit = 20
        if num_tracks < 20:
            limit = num_tracks - 1
        offset = 0
        finished = False
        while len(track_data) < num_tracks and finished is not True:
            tracks = [x['track']['artists'][0]['name'] + " " + x['track']['name'] for x in
                      self.spotify.current_user_saved_tracks(limit=limit, offset=offset)['items']]
            # if self.time_desired(x['added_at'].split("T")[0])
            offset += 20
            if len(tracks) == 0:
                finished = True
            track_data.extend([unicodedata.normalize('NFKD', x.replace(" ", "+").lower().replace("&", "and")).encode(
                'ascii', 'ignore').decode("utf-8") for x in tracks])
        return track_data

    def download_video(self, url):
        self.youtube_download.download([url])

    @staticmethod
    def run_multi(function, arg, workers=50):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            ex.map(function, arg)

    def clean_up(self):
        for x in self.get_all_downloaded_filenames():
            if x.split(".")[-1] not in [""]:
                os.remove(self.download_path + x)

    def run(self, track):
        download = Downloads()
        download.track_name = track
        url = self.search_for_youtube_url(track)
        download.url = url
        download.downloaded = False
        if url is not None:
            self.download_video(url)
            download.downloaded = True
        self.database_handler.insert(download)

    def multi_run(self):
        tracks = [x for x in self.get_starred_tracks(num_tracks=10000000) if
                  x not in self.database_handler.get_all_tracks()]
        if not tracks:
            print('All Caught Up')
        else:
            print(tracks)
            self.run_multi(self.run, tracks)


if __name__ == '__main__':
    spotify_downloader = SpotifyDownloader()
    spotify_downloader.multi_run()
    # spotify_downloader.download_video('https://www.youtube.com/watch?v=tAe2Q_LhY8g')