import cv2
import os
import time
import json
from config import ROBOFLOW_API_KEY, PROJECT_NAME, PROJECT_VERSION, DEDUPLICATION_TIME_THRESHOLD, IOU_THRESHOLD
from utils import iou, get_center_x
from datetime import datetime
import concurrent.futures
from roboflow import Roboflow

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
model = rf.workspace().project(PROJECT_NAME).version(PROJECT_VERSION).model

def is_duplicate(new_detection, log, timestamp):
    for past in reversed(log):
        if timestamp - past['timestamp'] > DEDUPLICATION_TIME_THRESHOLD:
            break
        if (
            past['label'] == new_detection['label'] and
            past['player'] == new_detection['player'] and
            iou(past['bbox'], new_detection['bbox']) > IOU_THRESHOLD
        ):
            return True
    return False


def run_inference_safe(image, timeout=10):
    def predict():
        return model.predict(image).json()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(predict)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print("[WARNING] Inference timed out.")
            return None

def run_inference_on_video(video_path, output_dir="inference_results", frame_interval=60):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    log = []

    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    txt_log_path = os.path.join(output_dir, f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(txt_log_path, "w") as log_file:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frame_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
                cv2.imwrite(frame_path, frame)

                result = run_inference_safe(frame_path)
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                if result and "predictions" in result:
                    for pred in result["predictions"]:
                        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
                        bbox = [x - w / 2, y - h / 2, w, h]
                        center_x = x
                        player = "p1" if center_x < video_width / 2 else "p2"

                        detection = {
                            "label": pred["class"],
                            "bbox": bbox,
                            "player": player,
                            "timestamp": timestamp
                        }

                        if not is_duplicate(detection, log, timestamp):
                            log.append(detection)
                            log_file.write(json.dumps(detection) + "\n")

            frame_count += 1

        # Now write the entire log with relative timestamps to the file
        txt_log_path = os.path.join(output_dir, f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(txt_log_path, "w") as log_file:
            for detection in log:
                log_file.write(json.dumps(detection) + "\n")

    cap.release()
    return log