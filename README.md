# 🏭 Factory Safety Detection System

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green.svg)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.8-red.svg)](https://mediapipe.dev)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ecf8e.svg)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


# 🏭 Factory Safety Detection System

Real-time computer vision system for monitoring worker safety in industrial environments. Detects improper hand placement and worker distraction, triggering instant alerts with automated incident logging.

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

## 🚀 Installation & Setup

### 📋 What You'll Need

- **Python 3.9+** → [Download here](https://python.org)
- **Git** → [Download here](https://git-scm.com)
- **Docker Desktop** → [Download here](https://docker.com) *(only for Metabase dashboard)*
- **A Webcam** → Any standard USB webcam works

---

### 🛠️ Step-by-Step Guide

**Step 1: Clone the repository**

```bash

1. Clone the Repository
    git clone https://github.com/palak172/FSDS-Deep-V2.git
    cd FSDS-Deep-V2

2. Create a Virtual Environment (Recommended)
This isolates project dependencies.
Windows:
    python -m venv venv
    .\venv\Scripts\activate

macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate

3. Install Dependencies
    pip install -r requirements.txt

5. Configure Environment Variables
Copy the example environment file and add your Supabase credentials:
    cp .env.example .env
Then open .env and fill in your details:
    SUPABASE_URL=https://your-project-ref.supabase.co
    SUPABASE_KEY=your_supabase_anon_key

5. Run the Application
Start the main safety monitoring system:
    python main.py

6. Start the Metabase Dashboard (Optional)
To view the analytics dashboard, run Metabase in a Docker container:
    docker run -d -p 3000:3000 --name metabase metabase/metabase
Then open your browser and go to http://localhost:3000.

Troubleshooting Common Issues
    pip install -r requirements.txt fails: Upgrade pip first:

    pip install --upgrade pip

Modules not found: Ensure your virtual environment is activated before running python main.py.

Docker command not found: Install and start Docker Desktop.

Camera not detected: Check your webcam connection and try changing CAMERA_INDEX in your .env file (e.g., 0, 1, or 2).

```

⚙️ Configuration
Create a .env file with:

-SUPABASE_URL=your_supabase_project_url

-SUPABASE_KEY=your_supabase_anon_key

-ALERT_THRESHOLD=0.7

-CAMERA_INDEX=0

-FPS_TARGET=30

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
