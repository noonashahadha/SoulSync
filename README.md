# 🧘 SoulSync — AI Workspace Wellness System

> Real-time posture detection and voice recommendation system built with MediaPipe, TensorFlow LSTM, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.12-orange?style=flat-square&logo=tensorflow)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.5-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![Accuracy](https://img.shields.io/badge/Model%20Accuracy-96%25-brightgreen?style=flat-square)

---

## 📖 What is SoulSync?

SoulSync is a real-time AI-powered wellness assistant that monitors your sitting posture through a webcam, classifies your physical state using a deep learning LSTM model, and delivers spoken recommendations to help you stay healthy and focused while working.

It watches you continuously and only speaks when it genuinely detects a problem — not at fixed intervals like most wellness apps.

---

## ✨ Features

-  **Real-time posture classification** 
-  **Custom LSTM model** 
-  **Voice recommendations** 
-  **Streamlit dashboard** 
-  **100% local** 
-  **96% validation accuracy** 

---

## 🗂️ Project Structure

```
SoulSync/
│
├── 1_data_generation/
│   └── collect_features.ipynb      # Records webcam landmarks to CSV
│
├── 2_model_training/
│   ├── soulsync_raw_data.csv        # Custom recorded dataset
│   └── soulsync_colab_training.ipynb  # LSTM training notebook (Google Colab)
│
└── 3_core_app/
    ├── models/
    │   ├── weight_0.npy ... weight_6.npy   # Trained model weights
    │   ├── scaler_mean.npy                  # Feature scaler
    │   └── scaler_scale.npy                 # Feature scaler
    ├── main_engine.py               # Live inference engine
    ├── recommender.py               # Voice recommendation logic
    └── app.py                       # Streamlit dashboard
```

---

## ⚙️ How It Works

| Stage | What happens |
|---|---|
| **1. Data Collection** | Webcam → MediaPipe Pose → 39 features per frame → CSV with labels |
| **2. Model Training** | CSV → 30-frame sliding windows → LSTM → trained weights |
| **3. Live Inference** | Webcam → MediaPipe → LSTM prediction every 1 second |
| **4. Recommendation** | Posture state + confidence → voice feedback via Windows SAPI |

---

### Installation

```bash
# Clone the repository
git clone https://github.com/noonashahadha/SoulSync.git
cd SoulSync

# Create virtual environment
python -m venv soul_venv
soul_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run 3_core_app/app.py
```

Then click **▶️ LAUNCH SOULSYNC CORE ENGINE** in the dashboard.

### Controls
| Key | Action |
|---|---|
| `0` | Set label — Balanced |
| `1` | Set label — Slumped |
| `2` | Set label — Restless |
| `R` | Toggle recording on/off |
| `Q` | Quit the engine |

---

## 📦 Tech Stack

| Library | Version | Purpose |
|---|---|---|
| TensorFlow | 2.12.0 | LSTM model training and inference |
| MediaPipe | 0.10.5 | Real-time pose landmark detection |
| OpenCV | latest | Webcam capture and overlay rendering |
| Streamlit | latest | Web dashboard UI |
| NumPy | 1.24.3 | Feature extraction and normalisation |
| win32com | latest | Windows native SAPI voice output |
| Protobuf | 3.20.3 | MediaPipe compatibility |

---

## 🎯 Posture States

| State | Description | 
|---|---|
|  **Balanced** | Upright, relaxed, healthy posture |
|  **Slumped** | Rounded back, dropped shoulders, fatigue | 
|  **Restless** | Constant movement, tension, distraction | 

---

## 👤 Author

**noonashahadha**
- GitHub: [@noonashahadha](https://github.com/noonashahadha)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
