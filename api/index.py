import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Vercel ONLY allows writing to the /tmp folder
UPLOAD_FOLDER = '/tmp'
OUTPUT_FOLDER = '/tmp'

# Try to initialize MediaPipe Pose; if unavailable, fall back to a no-op mode
USE_MEDIAPIPE = True
pose = None
mp_drawing = None
mp_pose = None  # Added global reference so it works inside functions

try:
    mp_solutions = getattr(mp, 'solutions', None)
    if mp_solutions is not None:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
        mp_drawing = mp.solutions.drawing_utils
    else:
        raise Exception('mp.solutions not available')
except Exception:
    USE_MEDIAPIPE = False
    pose = None
    mp_drawing = None

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360.0 - angle if angle > 180.0 else angle

def process_video_file(input_path, output_path, exercise_type):
    if not USE_MEDIAPIPE:
        try:
            import shutil
            shutil.copyfile(input_path, output_path)
            return []
        except Exception:
            return ["Processing disabled: MediaPipe not available on the server."]

    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or not fps:
        fps = 30

    # MP4V codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    warnings = []
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        timestamp_sec = round(frame_idx / fps, 2)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark

            try:
                if exercise_type == "squats":
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * width, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * height]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * width, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * height]
                    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * width, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * height]

                    angle = calculate_angle(hip, knee, ankle)

                    if angle > 100 and angle < 150:
                        cv2.putText(frame, "WARNING: SQUAT DEEPER!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                        warnings.append(f"At {timestamp_sec}s: Squat depth insufficient (Knee angle: {int(angle)}°)")

                elif exercise_type == "bicep_curls":
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * width, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * height]
                    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].value * width if hasattr(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value], 'x') else landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * width, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * height]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * width, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * height]

                    angle = calculate_angle(shoulder, elbow, wrist)

                    if angle > 60 and angle < 140:
                        cv2.putText(frame, "WARNING: INCOMPLETE REP!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                        warnings.append(f"At {timestamp_sec}s: Partial arm extension/flexion detected ({int(angle)}°)")
            except Exception:
                pass

        out.write(frame)

    cap.release()
    out.release()

    return list(dict.fromkeys(warnings))

@app.route('/api/upload', methods=['POST']) # Added /api/ prefix for Vercel routing
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
        
    file = request.files['video']
    exercise = request.form.get('exercise', 'squats')
    
    # Secure the filename to safely store in /tmp
    safe_name = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, safe_name)
    output_filename = f"processed_{safe_name}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    file.save(input_path)
    
    text_warnings = process_video_file(input_path, output_path, exercise)
    
    # Clean up the original input video to save temporary space
    if os.path.exists(input_path):
        os.remove(input_path)
    
    # Use dynamic host URL instead of hardcoded localhost:5000
    host_url = request.host_url.rstrip('/')
    
    return jsonify({
        "videoUrl": f"{host_url}/api/download/{output_filename}",
        "warnings": text_warnings
    })

@app.route('/api/download/<filename>') # Added /api/ prefix for Vercel routing
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# Vercel handles server execution automatically. This block is kept for local testing.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
