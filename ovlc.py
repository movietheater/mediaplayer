from sys import exit, argv

try:
	import vlc
	# https://github.com/oaubert/python-vlc/blob/master/generated/3.0/vlc.py
except ImportError:
	exit("Please install python-vlc lib using pip command: pip install python-vlc")

from configparser import ConfigParser
from urllib.parse import unquote
from os.path import join
from time import sleep
import ctypes
import os

__version__ = 1.7

class data:
	def __init__(self):
		self.file = join(join(os.getenv("appdata"), "ovlc"), "data.ini")
		self.config = ConfigParser()

	def prep(self):
		"""
		Ensures ovlc directory is created under '%appdata%' and a
		correct 'data.ini' file that can hold media information
		when player().remember() is being used.
		"""
		if not os.path.isdir(os.path.dirname(os.path.abspath(self.file))):
			try:
				os.mkdir(os.path.dirname(os.path.abspath(self.file)))
			except:
				return False

		try:
			with open(self.file, "r") as file:
				data = file.read()

			if not "[Data]" in data:
				try:
					os.remove(self.file)
				except Exception:
					return False
				else:
					f = open(self.file, "a")
					f.write("[Data]\nmedia =\ntime =\n")
					f.close()
		except FileNotFoundError:
			f = open(self.file, "a")
			f.write("[Data]\nmedia =\ntime =\n")
			f.close()

	def update(self, section, key, value):
		"""
		Update the data inside ini file
		"""	
		if self.config.read(self.file):
			self.config[section][key] = value
			with open(self.file, "w") as configfile:
				self.config.write(configfile)
			return True
		else:
			return False

	def media(self):
		"""
		Get media path
		"""	
		if self.config.read(self.file):
			return(self.config["Data"]["media"])
		else:
			return False

	def time(self):
		"""
		Get time in ms
		"""
		if self.config.read(self.file):
			return(self.config["Data"]["time"])
		else:
			return False

class player:
	def __init__(self):
		self.instance = vlc.Instance(["--video-on-top"])
		self.media_player = self.instance.media_player_new()
		self.media_player.set_fullscreen(True)
		self.media_file = ""

	def hwnd(self):
		"""
		Attempt to obtain hwnd of VLC output
		"""
		hwnd = ctypes.windll.user32.FindWindowW(None, u"VLC (Direct3D10 output)")
		if not hwnd:
			hwnd = ctypes.windll.user32.FindWindowW(None, u"VLC (Direct3D11 output)")
			if not hwnd:
				hwnd = ctypes.windll.user32.FindWindowW(None, u"VLC (Direct3D12 output)")

		if hwnd:
			return hwnd
		else:
			return False

	def remember(self):
		"""
		This function remembers where we stopped the media
		so if we want to replay it we can have that as a option
		"""
		ini = data()
		time = self.media_player.get_time() # Get the current movie time (in ms)
		if time:
			if ini.update("Data", "time", str(time)):
				yield(f"[settings] Current time ({time} ms) saved to config file")
			else:
				yield(f"[settings] Unable to save current time ({time} ms) in config file")
		if self.media_file:
			if ini.update("Data", "media", self.media_file):
				yield(f"[settings] Saved media path ({self.media_file}) in config file")
			else:
				yield(f"[settings] Unable to save media path ({self.media_file}) in config file")

	def listner(self):
		"""
		Hotkey listner that helps interacting with the player
		while being fullscreened
		"""
		hwnd = self.hwnd()
		if not hwnd == ctypes.windll.user32.GetForegroundWindow():
			pass
		else:
			VK_ESC = ctypes.windll.user32.GetAsyncKeyState(0x1B)
			VK_MEDIA_STOP = ctypes.windll.user32.GetAsyncKeyState(0xB2)
			if VK_ESC or VK_MEDIA_STOP:
				for r in self.remember():
					print(r)
				self.media_player.stop()
				exit()

			VK_MEDIA_NEXT_TRACK = ctypes.windll.user32.GetAsyncKeyState(0xB0)
			VK_MEDIA_PREV_TRACK = ctypes.windll.user32.GetAsyncKeyState(0xB1)
			if VK_MEDIA_PREV_TRACK:
				self.media_player.set_time(self.media_player.get_time() - 50000)
			if VK_MEDIA_NEXT_TRACK:
				self.media_player.set_time(self.media_player.get_time() + 50000)	

			VK_LEFT = ctypes.windll.user32.GetAsyncKeyState(0x25)
			VK_RIGHT = ctypes.windll.user32.GetAsyncKeyState(0x27)
			if VK_LEFT:
				self.media_player.set_time(self.media_player.get_time() - 10000)
			if VK_RIGHT:
				self.media_player.set_time(self.media_player.get_time() + 10000)		

			VK_SPACE = ctypes.windll.user32.GetAsyncKeyState(0x20)
			VK_MEDIA_PLAY_PAUSE = ctypes.windll.user32.GetAsyncKeyState(0xB3)
			if VK_SPACE or VK_MEDIA_PLAY_PAUSE:
				self.media_player.pause()

				while True:
					VK_SPACE = ctypes.windll.user32.GetAsyncKeyState(0x20)
					VK_MEDIA_PLAY_PAUSE = ctypes.windll.user32.GetAsyncKeyState(0xB3)
					VK_ESC = ctypes.windll.user32.GetAsyncKeyState(0x1B)
					if VK_SPACE or VK_MEDIA_PLAY_PAUSE:
						self.media_player.play()
						break
					if VK_ESC:
						for r in self.remember():
							print(r)
						self.media_player.stop()
						exit()

	def media(self):
		"""
		Set the media file
		"""
		if self.media_file:
			self.media_player.set_media(vlc.Media(self.media_file))
		else:
			return False

	def settings(self, language_spu=b"english", language_audio=b"english"):
		"""
		Attempt to auto adjust the subtitle and audio to the
		language provided in arguments. The argument needs to
		a bytes-like object.
		"""
		subs = self.media_player.video_get_spu_description()
		audio = self.media_player.audio_get_track_description()
		if subs:
			for s in subs:
				if language_spu in s[1].lower():
					if self.media_player.video_set_spu(s[0]) == 0:
						yield(f"[settings] Auto-adjusted subtitle to {s}")
						break
		if audio:
			for a in audio:
				if language_audio in a[1].lower():
					if self.media_player.audio_set_track(a[0]) == 0:
						yield(f"[settings] Auto-adjusted audio to {a}")
						break

	def play(self, remember=True):
		"""
		Play media and apply the audio/subs automaticly. Keep playing
		until the media ends or until ESC/VK_MEDIA_STOP is pressed.

		Argument:
			remember=True/False (toggles if the player should remember
			where it left off)

			Remarks: It only remembers the last played. Creates directory "%appdata%\ovlc" and
					 "data.ini" that contains media title and time in ms where media stopped.

					 When media reach the end, the media and time in data.ini
					 file will be deleted.
		"""
		self.media_player.play()

		if remember:
			ini = data()
			ini.prep()

			get_media = ini.media()
			get_time = ini.time()
			if get_media:
				if self.media_file in get_media:
					if get_time:
						self.media_player.set_time(int(get_time) - 8000)

		while True:
			sleep(1)
			state = self.media_player.is_playing()
			if state == 1:
				for settings in self.settings():
					print(settings)
				break

		while True:
			sleep(0.5)
			state = self.media_player.is_playing()
			if state == 1:
				self.listner()
			if state == 0:
				self.media_player.stop()
				if remember:
					ini.update("Data", "media", "")
					ini.update("Data", "time", "")
				exit()

if __name__ == "__main__":
	try:
		argument = argv[1]
	except IndexError:
		exit()
	else:
		if "ovlc:/" in argument:
			argument = argument.replace("ovlc://", "file:///")
			argument = unquote(argument)
		else:
			exit()

	try:
		p = player()
		p.media_file = argument
		p.media()
		p.play()
	except KeyboardInterrupt:
		exit()