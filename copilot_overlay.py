from time import sleep
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint, QSettings
from watchdog.observers import Observer
from edcopilot_manager import EDCoPilotSpeechManager
import sys
import random
import configparser
import os
import logging

# Configuration and state file paths
CONFIG_FILE = "config.ini"

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TransparentOverlay(QLabel):
	def __init__(self, config):
		super().__init__()

		self.config = config
		self.settings = QSettings("PNGCoPilot", "Overlay")
		self.load_config()
		self.load_state()
		self.speak = None #this is the speak function that will be passed in from the main function

		# Load images
		try:
			self.idle_image = QPixmap(self.idle_image_path)
			self.talking_image = QPixmap(self.talking_image_path)
		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to load images. {e}")
			logger.error(f"Error loading images: {e}")
			sys.exit(1)

		self.current_image = self.idle_image

		# Set up QLabel
		self.setPixmap(self.idle_image)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setAttribute(Qt.WA_NoSystemBackground)

		# Restore position, size, and state
		self.setGeometry(self.last_position.x(), self.last_position.y(), self.idle_image.width(), self.idle_image.height())
		self.scale_ratio = self.last_scale_ratio
		self.locked = self.last_locked_state
		self.update_image()

		# Drag variables
		self.drag_start_position = None

		# Talking state
		self.is_talking = False

		# Timer for continuous shaking
		self.animation_timer = QTimer(self)
		self.animation_timer.timeout.connect(self.perform_animation)

		self.start_animation()

		# Original position to reset after shaking
		self.original_pos = self.pos()

	def load_config(self):
		self.idle_image_path = self.config.get("OverlaySettings", "idle_image_path", fallback="idle.png")
		self.talking_image_path = self.config.get("OverlaySettings", "talking_image_path", fallback="talk.png")
		self.scaling_factor = self.config.getfloat("OverlaySettings", "scaling_factor", fallback=1.1)
		self.animation_interval = self.config.getint("OverlaySettings", "animation_interval", fallback=50)
		self.shake_intensity = self.config.getint("OverlaySettings", "shake_intensity", fallback=2)
		self.animation_delay = self.config.getfloat("OverlaySettings", "animation_delay", fallback=0.3)
		self.character = self.config.get("OverlaySettings", "character", fallback="<EDCoPilot>")

	def load_state(self):
		self.last_position = self.settings.value("last_position", QPoint(100, 100), type=QPoint)
		self.last_scale_ratio = self.settings.value("scale_ratio", 1.0, type=float)
		self.last_locked_state = self.settings.value("locked", False, type=bool)

	def save_state(self):
		self.settings.setValue("last_position", QPoint(self.x(), self.y()))
		self.settings.setValue("scale_ratio", self.scale_ratio)
		self.settings.setValue("locked", self.locked)

	def validate_config(self):
		required_settings = ["idle_image_path", "talking_image_path", "scaling_factor"]
		for setting in required_settings:
			if not self.config.has_option("OverlaySettings", setting):
				logger.error(f"Missing required setting: {setting}. Using fallback.")

	def closeEvent(self, event):
		self.save_state()
		event.accept()

	def switch_to_talking(self, character):
		if not self.is_talking and self.character == character:
			self.is_talking = True
			self.current_image = self.talking_image
			sleep(self.animation_delay)  # Delay because it tales copilot some time before it starts talking
			self.update_image()

	def switch_to_idle(self, character):
		if self.is_talking and self.character == character:
			self.is_talking = False
			self.current_image = self.idle_image
			self.update_image()

	def update_image(self):
		scaled_image = self.current_image.scaled(self.current_image.size() * self.scale_ratio, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.setPixmap(scaled_image)
		self.resize(scaled_image.size())
		self.setGeometry(self.x(), self.y(), scaled_image.width(), scaled_image.height())

	def start_animation(self):
		if not self.animation_timer.isActive():
			self.animation_timer.start(self.animation_interval)

	def stop_animation(self):
		if self.animation_timer.isActive():
			self.animation_timer.stop()
			self.move(self.original_pos)  # Reset to the original position

	def perform_animation(self):
		if self.is_talking:
			random_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
			random_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
			self.move(self.original_pos + QPoint(random_offset_x, random_offset_y))
		else:
			self.move(self.original_pos)  # Reset to the original position

	# Enable drag-and-drop functionality when not locked
	def mousePressEvent(self, event):
		if not self.locked and event.button() == Qt.LeftButton:
			self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
			event.accept()

	def mouseMoveEvent(self, event):
		if not self.locked and self.drag_start_position is not None and event.buttons() == Qt.LeftButton:
			self.move(event.globalPos() - self.drag_start_position)
			self.original_pos = self.pos() # Update the original position
			event.accept()

	def mouseReleaseEvent(self, event):
		if not self.locked and event.button() == Qt.LeftButton:
			self.drag_start_position = None
			event.accept()

	# Handle key presses for lock and close
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_L:  # Press 'L' to lock/unlock
			self.locked = not self.locked
			print(f"Overlay {'locked' if self.locked else 'unlocked'}.")
			event.accept()
		elif event.key() == Qt.Key_Q:  # Press 'Q' to close
			print("Closing overlay...")
			self.save_state()
			QApplication.instance().quit()
			event.accept()
		elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:  # '+' to scale up
			if self.locked:
				print("Cannot scale while locked.")
				event.ignore()
				return
			self.scale_ratio *= self.scaling_factor
			self.update_image()
			print(f"Scaled up: ratio={self.scale_ratio:.2f}")
			event.accept()
		elif event.key() == Qt.Key_Minus or event.key() == Qt.Key_Underscore:  # '-' to scale down
			if self.locked:
				print("Cannot scale while locked.")
				event.ignore()
				return
			self.scale_ratio /= self.scaling_factor
			self.update_image()
			print(f"Scaled down: ratio={self.scale_ratio:.2f}")
			event.accept()

def main():
	config = configparser.ConfigParser()

	# Load or create configuration
	if not os.path.exists(CONFIG_FILE):
		config["OverlaySettings"] = {			
			"idle_image_path": "idle.png",
			"talking_image_path": "talk.png",
			"scaling_factor": 1.0,
			"animation_interval": 50,
			"shake_intensity": 2,
			"animation_delay": 0.3
		}
		config["EDCoPilotSettings"] = {
			"edcopilot_dir": "C:\\EDCoPilot",
			"character": "<EDCoPilot>"
		}
		with open(CONFIG_FILE, "w") as config_file:
			config.write(config_file)

	config.read(CONFIG_FILE)

	app = QApplication(sys.argv)
	overlay = TransparentOverlay(config)

	# Validate configuration
	overlay.validate_config()

	edcopilot_dir = config.get("EDCoPilotSettings", "edcopilot_dir", fallback="C:\\EDCoPilot") 
	speech_status_file = os.path.join(edcopilot_dir, "working\\EDCoPilot.SpeechStatus.json")
	speech_request_file = os.path.join(edcopilot_dir, "EDCoPilot.request.txt")

	manager = EDCoPilotSpeechManager(speech_status_file, speech_request_file)	
	
	# Start watching for speech events
	manager.on_is_speaking = lambda character: overlay.switch_to_talking(character)
	manager.on_stop_speaking = lambda character: overlay.switch_to_idle(character)
	manager.start_watching()
	overlay.show()

	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
