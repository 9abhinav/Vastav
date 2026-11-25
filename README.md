# Real-Time Vehicle Speed & Traffic Violation Tracking System

An end-to-end, production-grade, software-only computer vision system that monitors recorded traffic/CCTV video feeds or webcam streams to detect, track, analyze, and enforce multiple traffic violations in real time with high-resolution visual evidence logging.

---

## 1. System Architecture & High-Level Design

```
[ CCTV / MP4 Video / Webcam / RTSP ]
                 │
                 ▼
     [ YOLOv8 Vehicle Detector ]
   (Car, Motorcycle, Bus, Truck)
                 │
                 ▼
     [ ByteTrack Tracker Engine ]
   (Persistent ID, Trajectories)
                 │
  ┌──────────────┼──────────────┬──────────────┐
  ▼              ▼              ▼              ▼
[Speed Estimator] [Red Light Det] [Wrong Way Det] [Lane Departure]
(Homography Quad) (Virtual Line)  (Vector Angle)  (Lane Polygons)
  │              │              │              │
  └──────────────┴──────┬───────┴──────────────┘
                        │
                        ▼
            [ Violation Trigger & Cooldown ]
                        │
                        ▼
      [ EasyOCR License Plate Recognition ]
            (Crop + CLAHE + Regex)
                        │
                        ▼
         [ Automated Evidence Capture ]
       (High-Res HUD Snapshot in /evidence)
                        │
                        ▼
         [ PostgreSQL / SQLite Database ]
                        │
                        ▼
       [ FastAPI REST & WebSocket Server ]
                        │
                        ▼
       [ React Cyberpunk Command Center ]
```

---

## 2. Key Features

- **Multi-Class Vehicle Detection**: Ultralytics YOLOv8 for precise bounding box detection of Cars, Motorcycles, Buses, and Trucks.
- **Persistent Trajectory Tracking**: ByteTrack algorithm assigns robust IDs, tracking centroids and bottom-center road contact coordinates across frames.
- **Perspective Homography Speed Estimation**:
  - Eliminates the naive "1 pixel = 1 meter" flaw by projecting road trapezoids into metric rectangular coordinates.
  - Computes `(distance_meters / dt_seconds) * 3.6` (km/h) with Exponential Moving Average (EMA) smoothing and outlier filtering.
- **Multi-Violation Detection**:
  1. **Over-Speeding**: Flags vehicles exceeding configurable speed limits (e.g. 60 km/h) with cooldown windows.
  2. **Virtual Red-Light Violation**: Detects stop-line breaches whenever the virtual traffic signal is `RED`.
  3. **Wrong-Way Driving**: Flags vehicles travelling opposite to the authorized flow direction via trajectory vector angles.
  4. **Lane Boundary Violation**: Detects vehicles straying outside designated lane polygons.
- **Automatic Number Plate Recognition (ANPR / OCR)**:
  - Uses EasyOCR on localized vehicle crops with bilateral filtering, CLAHE contrast enhancement, and regex formatting (`AP39XX1234`).
- **High-Resolution Evidence Capture**:
  - Saves annotated evidence images with violation telemetry banners, bounding boxes, plate tags, and timestamps to `evidence/`.
- **FastAPI REST & Real-Time WebSockets**:
  - Live MJPEG video stream with telemetry overlays (`/api/video/stream`).
  - Bi-directional WebSocket channel for instant violation alerts and traffic light state sync (`/api/ws/telemetry`).
  - Full CRUD for violations, vehicles, statistics, cameras, and system settings.
- **React Command Center Dashboard**:
  - Modern dark glassmorphism aesthetic with glowing cards, charts, and interactive virtual traffic signal controllers.
  - Interactive Calibration Canvas to visually adjust 4-point homography quads and stop-line positions.

---

## 3. Technology Stack

### Computer Vision & AI
- **Python 3.11+**
- **Ultralytics YOLOv8**
- **ByteTrack**
- **OpenCV 4.9+**
- **EasyOCR**
- **NumPy & Pandas & SciPy**

### Backend API
- **FastAPI & Uvicorn**
- **SQLAlchemy 2.0**
- **PostgreSQL / SQLite**
- **Pydantic v2 & Pydantic-Settings**
- **WebSockets**

### Frontend
- **React 18 & Vite**
- **Tailwind CSS**
- **Lucide Icons**
- **Recharts**
- **Axios**

### Deployment
- **Docker & Docker Compose**

---

## 4. Project Directory Structure

```
vehicle-violation-system/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point, static mounts, CORS
│   │   ├── config.py                # Environment configuration
│   │   ├── database.py              # SQLAlchemy engine & session factory
│   │   ├── models/                  # Vehicle, Violation, Camera, SystemSetting
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   ├── routers/                 # Health, Vehicles, Violations, Stats, Settings, Video, Stream
│   │   └── services/                # Video background worker & WebSocket manager
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai/
│   ├── pipeline.py                  # Master AI processing pipeline
│   ├── detection/yolo_detector.py   # YOLO vehicle detector
│   ├── tracking/bytetrack_tracker.py# ByteTrack manager & trajectories
│   ├── speed/speed_estimator.py     # Homography speed estimation & EMA smoothing
│   ├── violations/                  # Overspeed, Red Light, Wrong Way, Lane detectors
│   ├── ocr/plate_ocr.py             # EasyOCR & license plate image preprocessor
│   ├── calibration/camera_calibration.py # Perspective transformation matrix
│   ├── evidence/evidence_capture.py # Visual evidence snapshot generator
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/              # Sidebar, Navbar, LivePlayer, TrafficLight, EvidenceModal, Calibration
│   │   ├── pages/                   # Dashboard, LiveMonitoring, Violations, Vehicles, Analytics, Settings
│   │   ├── services/                # Axios API & WebSocket clients
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── videos/                          # Uploaded and demo video storage
├── evidence/                        # Violation evidence captures
├── models/                          # YOLOv8 weight cache
├── scripts/
│   ├── generate_demo_video.py       # Synthesizes realistic 720p traffic simulation
│   ├── setup_db.py                  # Initializes and seeds database
│   ├── run_backend.bat              # Quick-start backend on Windows
│   ├── run_frontend.bat             # Quick-start frontend on Windows
│   └── run_all.bat                  # One-click start all services
├── tests/                           # Unit and integration test suite
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 5. Installation & Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+ and npm**
- **Docker Desktop** (optional for containerized deployment)

### Local Environment Setup

1. **Clone and Navigate**:
   ```bash
   cd "d:\College imp\Projects\Vastav"
   ```

2. **Setup Python Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Backend & AI Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r ai/requirements.txt
   ```

4. **Initialize Database & Seed Configuration**:
   ```bash
   python scripts/setup_db.py
   ```

5. **Generate Synthetic Demo Traffic Video**:
   ```bash
   python scripts/generate_demo_video.py
   ```

6. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 6. How to Run

### Method A: One-Click Start (Windows)
Double-click `scripts\run_all.bat` or run:
```cmd
scripts\run_all.bat
```

### Method B: Manual Terminal Execution

**Terminal 1 (Backend)**:
```bash
.\venv\Scripts\activate
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

Open your browser at **`http://localhost:5173`**.
API documentation is available at **`http://localhost:8000/docs`**.

### Method C: Docker Compose
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/docs`

---

## 7. Demo Mode Walkthrough

1. Open `http://localhost:5173`.
2. Click **`START DEMO`** in the top navigation bar or navigate to **`Live Monitoring`**.
3. Watch the real-time annotated video stream with vehicle bounding boxes, velocity tags, and stop lines.
4. Test **Red Light Violation**:
   - In the top bar or Live Monitoring page, click the **`RED`** button on the virtual traffic signal widget.
   - Any car passing through the virtual stop line while RED is active will immediately trigger a citation, sound an alert, log in the database, and save visual evidence snapshot to `evidence/`.
5. Test **Over-Speeding**:
   - Fast vehicles (like the red sports car in the demo video) will automatically be flagged when exceeding 60 km/h.
6. Open **`Violations`** page to inspect citations, filter by plate or offense type, click **`Evidence`** to view the high-resolution snapshot modal, and update status (CONFIRMED / DISMISSED).

---

## 8. Speed Estimation & Calibration Guide

### Real-World Accuracy Notice
Accurate real-world vehicle speed estimation from a single camera requires camera calibration and known road reference points. A naive pixel displacement approach yields distorted results due to perspective foreshortening.

### Perspective Homography Calibration
1. Navigate to **`Settings & Calibration`** in the web dashboard.
2. Select **`Homography Quad (Speed)`**.
3. Drag the 4 corner handles `P1, P2, P3, P4` to align with the 4 corners of a known rectangular road segment.
4. Input the known physical road dimensions (e.g. `Width = 8.0 meters`, `Length = 30.0 meters`).
5. Click **`SAVE CALIBRATION`**. The system immediately recomputes the $3 \times 3$ perspective transformation matrix $H$:
   $$\mathbf{p}_{\text{metric}} = H \cdot \mathbf{p}_{\text{pixel}}$$
   Velocity is calculated as $\frac{\Delta d_{\text{metric}}}{\Delta t} \times 3.6 \text{ km/h}$.

---

## 9. Testing & Verification

Run the comprehensive automated test suite with `pytest`:

```bash
.\venv\Scripts\activate
pytest tests/ -v
```

---

## 10. Known Limitations & Future Enhancements

- **Lighting & Occlusion**: Severe weather or night-time low-contrast scenes can benefit from infrared cameras and night-vision YOLO fine-tuning.
- **3D Bounding Boxes**: Future versions can incorporate 3D bounding box estimation (e.g. YOLO3D) for height-aware vehicle centroids.
- **RTSP Live Hardware**: Architecture is fully ready for RTSP IP camera URLs directly input into the Cameras / Stream settings.
