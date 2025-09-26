import cv2
import time
import threading
from datetime import datetime
from flask import Flask, Response, render_template, jsonify
from ultralytics import YOLO

# --- Local Imports ---
import database

# -----------------------------------------------------------------------------------
# --- CONFIGURATION - YOU MUST EDIT THIS SECTION! ---
# -----------------------------------------------------------------------------------
VIDEO_SOURCE = r"C:\Users\kaviy\OneDrive\Desktop\safeZone\demo.mp4"         # Path to your video file
MODEL_WEIGHTS_PATH = r"C:\Users\kaviy\OneDrive\Desktop\safeZone\best (1).pt"          # Path to your trained YOLOv8 model (best.pt)
CONFIDENCE_THRESHOLD = 0.3              # Confidence level for detections (0.0 to 1.0)

# --- IMPORTANT: Class Names ---
# The exact names of your classes from your data.yaml file.
# Based on your log, these should be correct.
VEST_ON_CLASS_NAME = "Safety Vest"
VEST_OFF_CLASS_NAME = "NO-Safety Vest"
# -----------------------------------------------------------------------------------

# --- GLOBAL STATE & SETUP ---
app = Flask(__name__)
database.init_db() # Initialize the database when the app starts

live_data = {
    "workers_detected": 0,
    "compliant_workers": 0,
    "non_compliant_workers": 0,
}
data_lock = threading.Lock()

# --- MODEL SETUP ---
try:
    print("Loading YOLOv8 model...")
    model = YOLO(MODEL_WEIGHTS_PATH)
    class_names = model.names
    print(f"Model loaded successfully. Classes: {list(class_names.values())}")
except Exception as e:
    print(f"FATAL: Could not load YOLOv8 model. Error: {e}")
    exit()

# --- CORE LOGIC ---
def video_processing_and_streaming():
    """
    Main function that runs in a background thread.
    It reads frames, performs AI inference, analyzes for compliance,
    logs violations, and yields annotated frames for the live stream.
    """
    global live_data
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    last_violation_log_time = 0 # Cooldown to prevent logging too many violations at once

    while True:
        success, frame = cap.read()
        if not success:
            print("Video stream ended. Looping...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video
            continue
        
        # --- AI Inference ---
        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        annotated_frame = results[0].plot()

        # --- Analysis Logic (New, Simpler Logic) ---
        boxes = results[0].boxes
        compliant_count = 0
        non_compliant_count = 0
        
        for box in boxes:
            try:
                class_id = int(box.cls[0])
                class_name = class_names[class_id]
                
                if class_name == VEST_ON_CLASS_NAME:
                    compliant_count += 1
                elif class_name == VEST_OFF_CLASS_NAME:
                    non_compliant_count += 1
            except Exception as e:
                print(f"Warning: Could not process a detection. {e}")

        # --- Handle Violations ---
        if non_compliant_count > 0:
            current_time = time.time()
            # Log a violation only once every 5 seconds to avoid spam
            if current_time - last_violation_log_time > 5:
                last_violation_log_time = current_time
                
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot_filename = f"violation_{timestamp_str}.jpg"
                snapshot_path = f"static/snapshots/{snapshot_filename}"
                
                # We save the annotated frame so the snapshot has the boxes drawn on it
                cv2.imwrite(snapshot_path, annotated_frame)
                database.log_violation(snapshot_path)
                print(f"VIOLATION logged. Snapshot saved to {snapshot_path}")

        # Update the global live data dictionary safely
        with data_lock:
            live_data["workers_detected"] = compliant_count + non_compliant_count
            live_data["compliant_workers"] = compliant_count
            live_data["non_compliant_workers"] = non_compliant_count

        # --- Stream the Annotated Frame to the Browser ---
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if ret:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.01)

# --- FLASK WEB ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard_data')
def dashboard_data():
    with data_lock:
        data_to_send = live_data.copy()
    
    data_to_send.update(database.get_today_stats())
    data_to_send["recent_violations"] = database.get_recent_violations(limit=5)
    return jsonify(data_to_send)

@app.route('/video_feed')
def video_feed():
    return Response(video_processing_and_streaming(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting Flask server... Please open http://127.0.0.1:5001 in your browser.")
    app.run(host='0.0.0.0', port=5001, debug=False)

