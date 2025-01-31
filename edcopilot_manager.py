import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EDCoPilotSpeechManager:
	def __init__(self, speech_status_file, speech_request_file):
		self.speech_status_file = speech_status_file
		self.speech_request_file = speech_request_file
		self.observer = Observer()

		# Callbacks
		self.on_is_speaking = None  
		self.on_stop_speaking = None

		# Create the inner event handler class instance
		self.handler = self.SpeechStatusHandler(self)

	def start_watching(self):
		self.observer.schedule(self.handler, path=os.path.dirname(self.speech_status_file), recursive=False)
		self.observer.start()

	def stop_watching(self):
		self.observer.stop()
		self.observer.join()

	def write_speech_request(self, phrase_to_say):
		with open(self.speech_request_file, "w", encoding="utf-8") as file:
			file.write("SpeakThis:" + phrase_to_say)

	class SpeechStatusHandler(FileSystemEventHandler):

		def __init__(self, manager):
			self.manager = manager  # Link back to the main class

		def on_modified(self, event):
			if event.src_path == self.manager.speech_status_file:
				self.parse_speech_status()

		def parse_speech_status(self):
			try:
				with open(self.manager.speech_status_file, "r", encoding="utf-8") as status_file:
					data = json.load(status_file)

				#example data
				#{"timestamp": "2025-01-31T22:04:40Z", "Event": "PlayingSpeechFile", "Character": "<EDCoPilot>", "Text": "Thank for that. The silence was getting a bit awkward there.", "Duration": 3.912}
				event_value = data.get("Event", "Unknown")
				character = data.get("Character", "<EDCoPilot>")

				match event_value:
					case "PlayingSpeechFile":
						if self.manager.on_is_speaking:
							self.manager.on_is_speaking(character)
					case "FinishedSpeaking":
						if self.manager.on_stop_speaking:
							self.manager.on_stop_speaking(character)

			except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
				print(f"Error processing JSON: {e}")
