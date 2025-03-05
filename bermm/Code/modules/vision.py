import cv2
import mediapipe as mp
import logging
import os
import time

class VisionModule:
    def __init__(self, camera_index=0, mode="detection", display_window=True, 
                 save_frames=False, output_folder="captured_frames", frame_skip=1, 
                 detection_confidence=0.6):
        self.camera_index = camera_index
        self.mode = mode
        self.display_window = display_window
        self.save_frames = save_frames
        self.output_folder = output_folder
        self.frame_skip = frame_skip
        self.detection_confidence = detection_confidence
        
        if self.save_frames and not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        if self.mode == "detection":
            self.detector = self.mp_face_detection.FaceDetection(min_detection_confidence=self.detection_confidence)
        elif self.mode == "mesh":
            self.detector = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=self.detection_confidence
            )
        else:
            raise ValueError("Modo no reconocido. Usa 'detection' o 'mesh'.")

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("VisionModule inicializado en modo '%s' con cámara %d.", self.mode, self.camera_index)

    def process_camera_feed(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            logging.error("No se pudo abrir la cámara con índice %d.", self.camera_index)
            return
        
        frame_count = 0
        start_time = time.time()
        logging.info("Cámara abierta; iniciando procesamiento de frames.")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logging.warning("No se pudo leer el frame. Terminando procesamiento.")
                    break

                frame_count += 1
                if frame_count % self.frame_skip != 0:
                    continue

                original_frame = frame.copy()
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    logging.error("Error al convertir frame a RGB: %s", e)
                    continue

                process_start = time.time()
                if self.mode == "detection":
                    results = self.detector.process(rgb_frame)
                    if results and results.detections:
                        for detection in results.detections:
                            bboxC = detection.location_data.relative_bounding_box
                            h, w, _ = frame.shape
                            x = int(bboxC.xmin * w)
                            y = int(bboxC.ymin * h)
                            box_width = int(bboxC.width * w)
                            box_height = int(bboxC.height * h)
                            cv2.rectangle(frame, (x, y), (x + box_width, y + box_height), (0, 255, 0), 2)
                        logging.info("Frame %d: %d detecciones procesadas en %.2f segundos.",
                                     frame_count, len(results.detections), time.time() - process_start)
                    else:
                        logging.debug("Frame %d: No se detectaron rostros.", frame_count)
                elif self.mode == "mesh":
                    results = self.detector.process(rgb_frame)
                    if results and results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            for lm in face_landmarks.landmark:
                                h, w, _ = frame.shape
                                cx, cy = int(lm.x * w), int(lm.y * h)
                                cv2.circle(frame, (cx, cy), 1, (0, 255, 0), -1)
                        logging.info("Frame %d: Landmarks detectados en %.2f segundos.",
                                     frame_count, time.time() - process_start)
                    else:
                        logging.debug("Frame %d: No se detectaron landmarks.", frame_count)
                
                if self.save_frames:
                    frame_filename = os.path.join(self.output_folder, f"frame_{frame_count}.jpg")
                    try:
                        cv2.imwrite(frame_filename, original_frame)
                        logging.info("Frame %d guardado: %s", frame_count, frame_filename)
                    except Exception as e:
                        logging.error("Error al guardar el frame %d: %s", frame_count, e)
                
                if self.display_window:
                    try:
                        cv2.imshow("BERMM Vision", frame)
                    except Exception as e:
                        logging.error("Error al mostrar la ventana: %s", e)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        logging.info("Tecla 'q' presionada. Cerrando procesamiento.")
                        break

        except Exception as e:
            logging.error("Error durante el procesamiento de la cámara: %s", e)
        finally:
            cap.release()
            if self.display_window:
                cv2.destroyAllWindows()
            total_time = time.time() - start_time
            logging.info("Procesamiento finalizado. Total frames: %d, Tiempo transcurrido: %.2f segundos.", frame_count, total_time)

if __name__ == "__main__":
    vision = VisionModule(camera_index=0, mode="detection", display_window=True, save_frames=False, frame_skip=1, detection_confidence=0.6)
    vision.process_camera_feed()
