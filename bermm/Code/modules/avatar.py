import panda3d.core
from panda3d.core import AmbientLight, DirectionalLight
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
import pyttsx3
import mediapipe as mp
import cv2
import threading
import time

class AvatarModule(ShowBase):
    def __init__(self, camera_enabled=True):
        ShowBase.__init__(self)

        self.setup_lighting()

        self.avatar = Actor("models/avatar",
                            {"wave": "models/avatar_wave",
                             "talk": "models/avatar_talk"})
        self.avatar.reparentTo(self.render)
        self.avatar.setScale(1.5)
        self.avatar.setPos(0, 10, -2)

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        self.camera_enabled = camera_enabled
        if self.camera_enabled:
            self.mp_hands = mp.solutions.hands
            self.hand_detector = self.mp_hands.Hands()
            self.cap = cv2.VideoCapture(0)
            self.camera_thread = threading.Thread(target=self.process_camera_feed)
            self.camera_thread.start()

        self.avatar.loop("wave")

    def setup_lighting(self):
        ambient_light = AmbientLight("ambientLight")
        ambient_light.setColor((0.6, 0.6, 0.6, 1))
        ambient_node = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_node)

        directional_light = DirectionalLight("directionalLight")
        directional_light.setDirection((-1, -1, -1))
        directional_light.setColor((0.9, 0.9, 0.9, 1))
        directional_node = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_node)

    def speak(self, text):
        self.avatar.loop("talk")
        self.engine.say(text)
        self.engine.runAndWait()
        self.avatar.loop("wave")

    def process_camera_feed(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hand_detector.process(frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    thumb_tip = hand_landmarks.landmark[4]
                    index_tip = hand_landmarks.landmark[8]

                    if abs(thumb_tip.x - index_tip.x) < 0.05:
                        self.avatar.loop("wave")
                        print("👋 Gesto detectado: saludo")

            time.sleep(0.1)

    def change_avatar_color(self, part, color):
        if part == "skin":
            self.avatar.setColor(color[0], color[1], color[2], 1)
        elif part == "hair":
            self.avatar.find("**/Hair").setColor(color[0], color[1], color[2], 1)
        elif part == "eyes":
            self.avatar.find("**/Eyes").setColor(color[0], color[1], color[2], 1)
        print(f"Color de {part} cambiado a {color}")

    def cleanup(self):
        if self.camera_enabled:
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    app = AvatarModule(camera_enabled=True)
    app.run()
