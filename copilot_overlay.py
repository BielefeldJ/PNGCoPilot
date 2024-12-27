from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint
import sys
from sound_detector import SoundDetector
import random

# Configuration
idle_image_path = "idle.png"  	# Replace with your darkened PNG path
talking_image_path = "talk.png"	# Replace with your bright PNG path
scaling_factor = 1.1  			# Scale the image by this factor	

class TransparentOverlay(QLabel):
	def __init__(self):
		super().__init__()
		
		# Load images
		try:
			self.idle_image = QPixmap(idle_image_path)
			self.talking_image = QPixmap(talking_image_path)
		except Exception as e:
			print(f"Error loading images: {e}")
			sys.exit(1)

		self.current_image = self.idle_image

		# Initial scaling
		self.scale_ratio = 1.0

		# Set up the QLabel
		self.setPixmap(self.idle_image)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setAttribute(Qt.WA_NoSystemBackground)
		self.setGeometry(100, 100, self.idle_image.width(), self.idle_image.height())  # Position and size

		# Drag variables
		self.drag_start_position = None

		# Lock state
		self.locked = False

		# Talking state
		self.is_talking = False

		# Timer for continuous shaking
		self.animation_timer = QTimer(self)
		self.animation_timer.timeout.connect(self.perform_animation)

		self.start_animation()

		# Original position to reset after shaking
		self.original_pos = self.pos()

	def switch_to_talking(self):
		if not self.is_talking:
			self.is_talking = True
			self.current_image = self.talking_image
			self.update_image()

	def switch_to_idle(self):
		if self.is_talking:
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
			self.animation_timer.start(50)  # Adjust the interval for faster shaking (milliseconds)

	def stop_animation(self):
		if self.animation_timer.isActive():
			self.animation_timer.stop()
			self.move(self.original_pos)  # Reset to the original position

	def perform_animation(self):
		if self.is_talking:
			random_offset_x = random.randint(-2, 2)  # Random horizontal offset
			random_offset_y = random.randint(-2, 2)  # Random vertical offset
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
			QApplication.instance().quit()  # Close the application
			event.accept()
		elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:  # '+' to scale up
			if self.locked:
				print("Cannot scale while locked.")
				event.ignore()
				return
			self.scale_ratio *= scaling_factor
			self.update_image()
			print(f"Scaled up: ratio={self.scale_ratio:.2f}")
			event.accept()
		elif event.key() == Qt.Key_Minus or event.key() == Qt.Key_Underscore:  # '-' to scale down
			if self.locked:
				print("Cannot scale while locked.")
				event.ignore()
				return
			self.scale_ratio /= scaling_factor
			self.update_image()
			print(f"Scaled down: ratio={self.scale_ratio:.2f}")
			event.accept()
		elif event.key() == Qt.Key_W:  # 'W' to wiggle
			self.start_shaking()
			print("Wiggle animation triggered!")
			event.accept()

def main():
	app = QApplication(sys.argv)

	overlay = TransparentOverlay()

	detector = SoundDetector(threshold=4000, sample_rate=30)
	detector.on_sound_detected = lambda volume: overlay.switch_to_talking()
	detector.on_no_sound_detected = lambda volume: overlay.switch_to_idle()

	overlay.show()
	detector.start()

	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
