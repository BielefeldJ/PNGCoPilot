import pyaudio
import numpy as np
import threading
import time

class SoundDetector:
	def __init__(self, device_index=None, threshold=500, sample_rate=30):
		"""
		Initialize the SoundDetector.
		
		:param device_index: Index of the audio input device. If None, will prompt the user to select a device.
		:param threshold: Volume threshold to detect sound.
		:param sample_rate: Number of times per second to process audio.
		"""
		self.device_index = int(device_index) if device_index is not None and device_index != "" else None
		self.threshold = threshold
		self.sample_rate = sample_rate  # Samples per second
		self._running = False
		self.on_sound_detected = None
		self.on_no_sound_detected = None

		if self.device_index is None or self.device_index == "":
			self.device_index = self._select_device()

	def _select_device(self):
		"""List available devices and let the user select one."""
		p = pyaudio.PyAudio()
		print("Available audio input devices:")
		available_devices = []
		for i in range(p.get_device_count()):
			device_info = p.get_device_info_by_index(i)
			if device_info["maxInputChannels"] > 0:
				available_devices.append((i, device_info["name"]))
				print(f"{i}: {device_info['name']}")

		p.terminate()

		if not available_devices:
			raise RuntimeError("No audio input devices found.")

		device_index = None
		while device_index is None:
			try:
				user_choice = int(input("Enter the device index to use: "))
				if user_choice < 0 or user_choice >= len(available_devices):
					print("Invalid index. Please try again.")
				else:
					device_index = available_devices[user_choice][0]
			except ValueError:
				print("Invalid input. Please enter a valid device index.")
		return device_index

	def _process_audio(self):
		"""Internal method to process audio in a thread."""
		CHUNK = 1024  # Number of audio samples per frame
		FORMAT = pyaudio.paInt16  # Format of audio data
		CHANNELS = 1  # Single audio channel (mono)
		RATE = 44100  # Sampling rate in Hz

		p = pyaudio.PyAudio()

		# Open audio stream
		stream = p.open(format=FORMAT,
						channels=CHANNELS,
						rate=RATE,
						input=True,
						input_device_index=self.device_index,
						frames_per_buffer=CHUNK)

		print("SoundDetector started. Listening for sound...")
		try:
			while self._running:
				start_time = time.time()

				# Read audio data
				data = stream.read(CHUNK, exception_on_overflow=False)
				# Convert data to numpy array
				audio_data = np.frombuffer(data, dtype=np.int16)
				# Compute the volume
				volume = np.linalg.norm(audio_data)

				# Emit events based on the volume
				if volume > self.threshold and self.on_sound_detected:
					self.on_sound_detected(volume)
				elif volume <= self.threshold and self.on_no_sound_detected:
					self.on_no_sound_detected(volume)

				# Wait to maintain the sample rate
				elapsed_time = time.time() - start_time
				time.sleep(max(0, 1 / self.sample_rate - elapsed_time))
		finally:
			stream.stop_stream()
			stream.close()
			p.terminate()

	def start(self):
		"""Start the sound detection."""
		if not self._running:
			self._running = True
			self._thread = threading.Thread(target=self._process_audio, daemon=True)
			self._thread.start()

	def stop(self):
		"""Stop the sound detection."""
		self._running = False
		if self._thread:
			self._thread.join()
	
	def get_device_index(self):
		return self.device_index

# Example usage
if __name__ == "__main__":
	def sound_detected_handler(volume):
		print(f"Sound detected! Volume: {volume:.2f}")

	def no_sound_detected_handler(volume):
		print(f"No sound detected. Volume: {volume:.2f}")

	# Instantiate and use the SoundDetector
	detector = SoundDetector(threshold=500)
	detector.on_sound_detected = sound_detected_handler
	detector.on_no_sound_detected = no_sound_detected_handler

	try:
		detector.start()
		input("Press Enter to stop...\n")
	finally:
		detector.stop()
