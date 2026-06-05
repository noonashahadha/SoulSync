"""

Fuses live webcam pose detection with the trained LSTM model
to classify posture states in real time and trigger audio recommendations.

Requirements:
    pip install mediapipe==0.10.5 opencv-python tensorflow==2.13.0 numpy==1.24.3 pyttsx3 protobuf==3.20.3

"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2                   
import mediapipe as mp       
import numpy as np          
import tensorflow as tf      
import collections           # For buffering frames(deque)
import time                  # For timing predictions and cooldowns
import os                    
import math
import threading             # For non-blocking speech (run speech without freezing UI)
from tensorflow.keras import layers, models         # For building the model architecture
from recommender import Recommender                 # For generating and speaking recommendations


BASE_DIR   = os.path.dirname(os.path.abspath(__file__)) 
MODELS_DIR = os.path.join(BASE_DIR, "models")
MEAN_PATH  = os.path.join(MODELS_DIR, "scaler_mean.npy")
SCALE_PATH = os.path.join(MODELS_DIR, "scaler_scale.npy")


# Build model and load weights 
print("Loading model........")

model = models.Sequential([
                    layers.Input(shape=(30, 39)),
                    layers.LSTM(128, dropout=0.3),
                    layers.Dense(64, activation='relu'),
                    layers.Dropout(0.3),
                    layers.Dense(3, activation='softmax')])

model.build(input_shape=(None, 30, 39))


# Load individual weight files saved during training 
weights = []
i = 0

while True:
    path = os.path.join(MODELS_DIR, f'weight_{i}.npy')
    if not os.path.exists(path):
        break
    weights.append(np.load(path, allow_pickle=False))
    i += 1

model.set_weights(weights)     # Set the loaded weights into the model
print(f"Model loaded. ({i} weight arrays)")


TRACKED_LANDMARKS = {
                "nose":           0,
                "left_shoulder":  11,
                "right_shoulder": 12,
                "left_elbow":     13, 
                "right_elbow":    14,
                "left_wrist":     15, 
                "right_wrist":    16,
                "left_hip":       23, 
                "right_hip":      24}

WRIST_NOSE_THRESHOLD = 0.25


def euclidean(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def extract_features(landmarks):

    """Extract the same 39 features used during training"""
    lm  = landmarks.landmark
    row = []

    for index in TRACKED_LANDMARKS.values():
        pt = lm[index]
        row += [round(pt.x, 6), round(pt.y, 6), round(pt.z, 6), round(pt.visibility, 4)]

    nose, lw, rw = lm[0], lm[15], lm[16]
    l_dist = round(euclidean(lw, nose), 6)
    r_dist = round(euclidean(rw, nose), 6)
    near   = int(l_dist < WRIST_NOSE_THRESHOLD or r_dist < WRIST_NOSE_THRESHOLD)
    row   += [l_dist, r_dist, near]

    return np.array(row, dtype=np.float32)


# Load scaler parameters for standardisation 
scaler_mean = np.load(MEAN_PATH)
scaler_std  = np.load(SCALE_PATH)

def standardise(features):
    return (features - scaler_mean) / scaler_std


CLASS_NAMES  = {0: "Balanced", 1: "Slumped", 2: "Restless"}
CLASS_COLORS = {
            "Balanced": (142, 196, 114),  
            "Slumped":  (102, 140, 242),  
            "Restless": (214, 171, 107),  
            "Detecting.....": (180, 180, 180)} 

def draw_overlay(frame, state, confidence, last_recommendation):
    h, w = frame.shape[:2]
    color = CLASS_COLORS.get(state, (180, 180, 180))
    
    overlay = frame.copy()  # Create a copy to draw the semi-transparent background

    cv2.rectangle(overlay, (0, 0), (w, 85), (35, 30, 30), -1)

    # Blend the overlay with the original frame to create a semi-transparent effect
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)  

    cv2.putText(frame, f"ANALYSIS: {state.upper()}",
                (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 2, cv2.LINE_AA)
    cv2.putText(frame, f"Confidence Score: {confidence:.1%}",
                (20, 65), cv2.FONT_HERSHEY_DUPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
    
    
    if last_recommendation:
        # re-verify layout copies for the footer segment
        footer_overlay = frame.copy()

        cv2.rectangle(footer_overlay, (0, h - 55), (w, h), (40, 35, 35), -1)
        cv2.addWeighted(footer_overlay, 0.90, frame, 0.10, 0, frame)

        cv2.line(frame, (0, h - 55), (w, h - 55), color, 1, cv2.LINE_AA)

        max_char_len = int(w * 0.11)
        display_text = last_recommendation
        if len(display_text) > max_char_len:
            display_text = display_text[:max_char_len] + "..."

        # Render Recommendation text using an organic, readable layout accent tone
        cv2.putText(frame, f"RECOMMENDATION: {display_text}", (20, h - 22), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.45, (225, 235, 220), 1, cv2.LINE_AA)

    # Minimalist, out-of-the-way control exit hint
    cv2.putText(frame, "[Q] EXIT ENGINE", (w - 125, h - 70), 
                cv2.FONT_HERSHEY_DUPLEX, 0.4, (120, 120, 120), 1, cv2.LINE_AA)


WINDOW_SIZE          = 30
PREDICTION_INTERVAL  = 1.0       # predicts once every second
COOLDOWN_SECONDS     = 30        # Gap between spoken recommendations
CONFIDENCE_THRESHOLD = 0.75      # only speak if confidence >= 75%


def main():

    mp_pose = mp.solutions.pose
    mp_draw = mp.solutions.drawing_utils

    recommender     = Recommender()
    frame_buffer    = collections.deque(maxlen=WINDOW_SIZE)
    last_pred_time  = 0.0          # For timing predictions
    last_speak_time = 0.0          # For timing spoken recommendations
    current_state   = "Detecting....."
    current_conf    = 0.0 
    last_rec_text   = ""   # To display the last spoken recommendation on the overlay

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("SoulSync running. Press Q to quit.\n")

    with mp_pose.Pose(
                    min_detection_confidence=0.6,
                    min_tracking_confidence=0.6,
                    model_complexity=1 ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame   = cv2.flip(frame, 1)
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                
                mp_draw.draw_landmarks( frame,
                            results.pose_landmarks,
                            mp_pose.POSE_CONNECTIONS,
                            mp_draw.DrawingSpec(color=(230, 230, 230),thickness=-1,circle_radius=2),
                            mp_draw.DrawingSpec(color=(140, 140, 140),thickness=1))


                # Extract features, standardise, and buffer them for prediction
                features = extract_features(results.pose_landmarks)
                features = standardise(features)
                frame_buffer.append(features)

                # Predict every PREDICTION_INTERVAL seconds
                now = time.time()      # Current time in seconds since epoch
                if (len(frame_buffer) == WINDOW_SIZE and
                        now - last_pred_time >= PREDICTION_INTERVAL):

                    last_pred_time = now
                    sequence   = np.array(frame_buffer)[np.newaxis, ...]  # (1, 30, 39)
                    probs      = model.predict(sequence, verbose=0)[0]
                    pred_idx   = int(np.argmax(probs))
                    confidence = float(probs[pred_idx])

                    current_state = CLASS_NAMES[pred_idx]
                    current_conf  = confidence

                    print(f"[{time.strftime('%H:%M:%S')}] {current_state} ({confidence:.1%})")

                    # Speak recommendation if confident + cooldown passed
                    if (confidence >= CONFIDENCE_THRESHOLD and
                                    now - last_speak_time >= COOLDOWN_SECONDS):

                        msg = recommender.get_message(current_state)
                        if msg:
                            last_speak_time = now
                            last_rec_text   = msg
                            threading.Thread(target=recommender.speak,
                                            args=(msg,),daemon=True).start()

            draw_overlay(frame, current_state, current_conf, last_rec_text)

            cv2.imshow("SoulSync — Live", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("SoulSync stopped")


if __name__ == "__main__":
    main()