# 🏭 Factory Safety Detection System

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green.svg)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.8-red.svg)](https://mediapipe.dev)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ecf8e.svg)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


# 🏭 Factory Safety Detection System

Real-time computer vision system for monitoring worker safety in industrial environments. Detects improper hand placement and worker distraction, triggering instant alerts with automated incident logging.

## 📊 Demo

| Real-time Detection | Analytics Dashboard |
|---------------------|---------------------|
| [Add screenshot of detection] | [Add screenshot of Metabase] |

## ✨ Features

- 🚨 **Real-time violation detection** - 30 FPS continuous monitoring
- 🖐️ **Pose & hand landmark detection** using MediaPipe AI
- 📝 **Automated incident logging** to Supabase database
- 📈 **Analytics dashboard** with Metabase for safety metrics
- ⚡ **<100ms alert latency** for instant response
- 🔧 **Scalable** to multiple camera feeds

## 🎯 Problem Solved

Factory workers face safety risks from improper hand placement near hazardous zones and distraction. Manual incident reporting is slow, error-prone, and often misses violations. This system automates real-time monitoring with instant alerts.

## 🏗️ Architecture

Camera Feed → OpenCV Capture → MediaPipe Processing → Violation Detection → Alert Trigger → Supabase Logging → Metabase Dashboard

## 🔧 Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python 3.9+ |
| Computer Vision | OpenCV, MediaPipe |
| Database | Supabase (PostgreSQL) |
| Analytics | Metabase |
| Version Control | Git |

## 📋 Requirements

- Python 3.9 or higher
- Webcam (or video file for testing)
- Supabase account (free tier works)
- Metabase instance (local or cloud)

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/palak172/FSDS-Deep-V2.git
cd FSDS-Deep-V2

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Edit .env with your Supabase credentials

# Run the application
python main.py

⚙️ Configuration
Create a .env file with:

SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ALERT_THRESHOLD=0.7
CAMERA_INDEX=0
FPS_TARGET=30

📁 Project Structure

factory-safety-detection/

```
FSDS-Deep-V2/
├── main.py                 # Entry point
├── config.json            # Configuration
├── .env                   # API keys (excluded from Git)
├── requirements.txt       # Dependencies
│
├── core/
│   ├── camera_manager.py  # Camera handling
│   └── safety_monitor.py  # Main safety logic
│
├── detection/
│   ├── face_mesh_detector.py  # Face detection + calibration
│   └── hand_mesh_detector.py  # Hand tracking
│
├── zone/
│   ├── zone_manager.py    # Zone logic
│   └── zone_drawer.py     # Zone visualization
│
├── visualization/
│   ├── status_panel.py    # Status display
│   ├── safety_overlay.py  # Colored borders
│   ├── input_overlay.py   # Session input
│   └── hand_drawer.py     # Hand drawing
│
├── utils/
│   ├── logger.py          # Logging
│   └── internet_checker.py # Offline/online detection
│
├── database/
│   └── local_db_manager.py # SQLite offline storage
│
├── data/
│   └── factory_safety.db   # Local SQLite database
│
└── screenshots/
    ├── screenshot_safe.png
    ├── screenshot_warning.png
    └── screenshot_critical.png
```

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

📝 License
Distributed under the MIT License. See LICENSE for more information.

📧 Contact
Palak Arora - ar.palak0217@gmail.com - https://www.linkedin.com/in/palak-arora172/

Project Link: https://github.com/palak172/FSDS-Deep-V2

🙏 Acknowledgements
MediaPipe for pose estimation

OpenCV community

Supabase for database hosting
