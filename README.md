# Implementation of Multi-Vector Attack Detection and Classification Using Machine Learning for Improved Network Security

## Overview

This implementation plan outlines the development of a complete intrusion detection system (IDS) for a final-year university project. The system will:

- Use the **CICIDS2017** dataset for training and evaluation
- Implement a **Random Forest classifier** for multi-class attack detection
- Detect 4 attack types: **Benign**, **DDoS**, **Brute Force**, and **SQL Injection**
- Achieve **≥95% accuracy**
- Provide **real-time detection** via **live network interface capture** (primary) and PCAP file analysis (secondary)
- Deploy a **FastAPI web dashboard** for monitoring and alerts

---

## User Review Required

> [!NOTE]
> **Dataset Availability**: The CICIDS2017 dataset is already available locally in Parquet format in the `cicids2017/` directory. Available files:
> - `Benign-Monday-no-metadata.parquet` → **Benign** class
> - `Bruteforce-Tuesday-no-metadata.parquet` → **Brute Force** class
> - `DDoS-Friday-no-metadata.parquet` → **DDoS** class
> - `WebAttacks-Thursday-no-metadata.parquet` → **SQL Injection** class (contains SQL injection attacks)
> - Other files (Botnet, DoS, Infiltration, Portscan) will be excluded from this project

> [!IMPORTANT]
> **Class Extraction**: CICIDS2017 contains multiple attack types. The system will filter and extract only the 4 required classes (Benign, DDoS, Brute Force, SQL Injection). Other attack types in the dataset will be excluded.

> [!IMPORTANT]
> **Real-time Detection Scope**: The system will capture and analyze **live network traffic** from network interfaces as the primary detection method. This requires:
> - Running with **administrator/elevated privileges** on Windows
> - **Npcap** driver installation (WinPcap successor for Windows)
> - Network interface selection capability
> - PCAP file analysis will be available as a secondary feature for forensic analysis

---

## Proposed Changes

### Component 1: Project Structure & Dataset Acquisition

#### [NEW] [requirements.txt](file:///d:/Uni/FYP/multivector_ml_ids/requirements.txt)
Python backend dependencies:
- `pandas`, `numpy` for data manipulation
- `pyarrow` or `fastparquet` for reading Parquet files
- `scikit-learn` for ML pipeline and Random Forest
- `imbalanced-learn` for SMOTE (class balancing)
- `scapy` for packet capture and parsing
- `pyshark` for Wireshark-compatible packet analysis (uses tshark)
- `fastapi`, `uvicorn`, `websockets` for web dashboard and real-time communication
- `matplotlib`, `seaborn` for visualizations
- `joblib` for model persistence

#### [NEW] [frontend/package.json](file:///d:/Uni/FYP/multivector_ml_ids/frontend/package.json)
React TypeScript frontend dependencies:
- `react`, `react-dom` for UI framework
- `typescript` for type safety
- `tailwindcss` for styling
- `recharts` or `chart.js` for real-time graphs and visualizations
- `socket.io-client` for WebSocket communication
- `vite` for fast development and build tooling

#### [NEW] [docs/npcap_installation.md](file:///d:/Uni/FYP/multivector_ml_ids/docs/npcap_installation.md)
Npcap driver installation guide for Windows:
- Download and installation steps
- WinPcap API compatibility mode
- Administrator privilege requirements

#### [NEW] [src/data/dataset_loader.py](file:///d:/Uni/FYP/multivector_ml_ids/src/data/dataset_loader.py)
CICIDS2017 Parquet dataset loader:
- Load existing Parquet files from `cicids2017/` directory
- Map files to attack classes:
  - `Benign-Monday-no-metadata.parquet` → label as "Benign"
  - `Bruteforce-Tuesday-no-metadata.parquet` → label as "Brute Force"
  - `DDoS-Friday-no-metadata.parquet` → label as "DDoS"
  - `WebAttacks-Thursday-no-metadata.parquet` → filter for SQL Injection attacks, label as "SQL Injection"
- Merge all dataframes into unified dataset
- Add `attack_type` column with 4-class labels
- Display dataset statistics (samples per class, total features)

#### [NEW] [config/config.py](file:///d:/Uni/FYP/multivector_ml_ids/config/config.py)
Configuration management:
- Dataset paths
- Model hyperparameters
- API settings
- Feature engineering parameters

---

### Component 2: Data Preprocessing & Feature Engineering

#### [NEW] [src/preprocessing/data_cleaner.py](file:///d:/Uni/FYP/multivector_ml_ids/src/preprocessing/data_cleaner.py)
Data cleaning pipeline:
- Handle missing values (imputation or removal)
- Remove duplicate rows
- Filter corrupted entries
- Extract 4 target classes from CICIDS2017 labels
- Balance classes using SMOTE or undersampling (with justification)

#### [NEW] [src/preprocessing/feature_engineer.py](file:///d:/Uni/FYP/multivector_ml_ids/src/preprocessing/feature_engineer.py)
Feature engineering pipeline:
- Min-Max normalization (0-1 scaling)
- PCA dimensionality reduction
- Feature selection and variance analysis
- Document retained variance (target: 95%+)
- Save scaler and PCA transformer for inference

#### [NEW] [notebooks/eda.ipynb](file:///d:/Uni/FYP/multivector_ml_ids/notebooks/eda.ipynb)
Exploratory Data Analysis:
- Dataset statistics and distributions
- Class imbalance visualization
- Feature correlation analysis
- Missing value analysis

---

### Component 3: Random Forest Model Training

#### [NEW] [src/models/random_forest_trainer.py](file:///d:/Uni/FYP/multivector_ml_ids/src/models/random_forest_trainer.py)
Random Forest training pipeline:
- Train-test split (80/20 or 70/30)
- RandomForestClassifier implementation
- Hyperparameter tuning using GridSearchCV:
  - `n_estimators`: [100, 200, 300]
  - `max_depth`: [10, 20, 30, None]
  - `min_samples_split`: [2, 5, 10]
  - `min_samples_leaf`: [1, 2, 4]
- Cross-validation (5-fold)
- Save best model to `models/random_forest_model.pkl`

---

### Component 4: Model Evaluation

#### [NEW] [src/evaluation/evaluator.py](file:///d:/Uni/FYP/multivector_ml_ids/src/evaluation/evaluator.py)
Comprehensive model evaluation:
- Calculate accuracy, precision, recall, F1-score (macro and per-class)
- Generate confusion matrix
- Create classification report
- Save metrics to JSON for thesis documentation
- Generate visualizations (confusion matrix heatmap, ROC curves)

#### [NEW] [results/evaluation_report.json](file:///d:/Uni/FYP/multivector_ml_ids/results/evaluation_report.json)
Thesis-ready evaluation metrics in structured format

#### [NEW] [results/confusion_matrix.png](file:///d:/Uni/FYP/multivector_ml_ids/results/confusion_matrix.png)
Confusion matrix visualization

---

### Component 5: Real-Time Traffic Capture & Inference (CORE COMPONENT)

#### [NEW] [src/capture/live_capture.py](file:///d:/Uni/FYP/multivector_ml_ids/src/capture/live_capture.py)
**Live network interface capture (PRIMARY)**:
- List available network interfaces using Scapy
- Capture live packets from selected interface (requires admin privileges)
- Use both Scapy and pyshark (Wireshark-compatible) for packet capture
- Implement packet sniffing with configurable filters
- Buffer packets for flow aggregation
- Extract flow-level features in real-time:
  - Flow duration, packet count, byte count
  - Protocol flags (SYN, ACK, FIN, RST, PSH, URG)
  - Inter-arrival times, packet size statistics
  - Forward/backward packet ratios
- Thread-safe packet queue for continuous capture

#### [NEW] [src/capture/pcap_parser.py](file:///d:/Uni/FYP/multivector_ml_ids/src/capture/pcap_parser.py)
**PCAP file processing (SECONDARY - for forensic analysis)**:
- Parse pre-captured PCAP files using Scapy/pyshark
- Extract same flow-level features as live capture
- Batch processing mode for historical analysis
- Export results to CSV

#### [NEW] [src/inference/feature_extractor.py](file:///d:/Uni/FYP/multivector_ml_ids/src/inference/feature_extractor.py)
Flow feature extraction:
- Convert raw packets to CICIDS2017-compatible features
- Handle TCP/UDP/ICMP protocols
- Calculate statistical features (mean, std, min, max)
- Maintain flow state tables (5-tuple: src_ip, dst_ip, src_port, dst_port, protocol)

#### [NEW] [src/inference/predictor.py](file:///d:/Uni/FYP/multivector_ml_ids/src/inference/predictor.py)
Real-time prediction engine:
- Load trained Random Forest model
- Load preprocessing transformers (scaler, PCA)
- Transform extracted features to model input
- Generate predictions with confidence scores
- Return attack type, probability distribution, and timestamp
- Thread-safe prediction queue for concurrent processing

---

### Component 6: FastAPI Backend + React TypeScript Dashboard

#### Backend (FastAPI + WebSockets)

##### [NEW] [src/api/main.py](file:///d:/Uni/FYP/multivector_ml_ids/src/api/main.py)
FastAPI application with WebSocket support:
- Initialize FastAPI app with CORS for React frontend
- Load ML model and preprocessors on startup
- WebSocket manager for real-time alert broadcasting
- In-memory data structures (deque) for recent alerts and statistics
- Background task for live capture management

##### [NEW] [src/api/routes/capture.py](file:///d:/Uni/FYP/multivector_ml_ids/src/api/routes/capture.py)
Live capture control endpoints:
- `GET /api/interfaces` - List available network interfaces
- `POST /api/capture/start` - Start live capture on selected interface
- `POST /api/capture/stop` - Stop live capture
- `GET /api/capture/status` - Get capture status (running/stopped, packets captured)

##### [NEW] [src/api/routes/prediction.py](file:///d:/Uni/FYP/multivector_ml_ids/src/api/routes/prediction.py)
Prediction and analysis endpoints:
- `POST /api/predict/pcap` - Upload PCAP file for batch analysis (secondary feature)
- `GET /api/alerts` - Get recent alerts (paginated, from in-memory deque)
- `GET /api/stats` - Real-time statistics (attack distribution, detection rate)
- `GET /api/export/csv` - Export historical alerts to CSV

##### [NEW] [src/api/websocket/alert_handler.py](file:///d:/Uni/FYP/multivector_ml_ids/src/api/websocket/alert_handler.py)
WebSocket handler for real-time alerts:
- `/ws/alerts` - WebSocket endpoint for live alert streaming
- Broadcast predictions to all connected clients
- JSON format: `{timestamp, attack_type, confidence, src_ip, dst_ip, protocol}`

##### [NEW] [src/api/services/data_manager.py](file:///d:/Uni/FYP/multivector_ml_ids/src/api/services/data_manager.py)
In-memory data management:
- `collections.deque` for recent alerts (max 1000 entries)
- Real-time statistics aggregation (attack counts, hourly rates)
- CSV logging service for historical analysis
- Automatic CSV rotation (daily files)

---

#### Frontend (React + TypeScript + Tailwind CSS)

##### [NEW] [frontend/src/App.tsx](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/App.tsx)
Main React application:
- Dashboard layout with sidebar navigation
- Real-time alert feed component
- Statistics overview panel
- Network interface selector

##### [NEW] [frontend/src/components/LiveCapture.tsx](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/components/LiveCapture.tsx)
Live capture control panel:
- Network interface dropdown (fetched from `/api/interfaces`)
- Start/Stop capture buttons
- Capture status indicator (running/stopped)
- Packet count display

##### [NEW] [frontend/src/components/AlertFeed.tsx](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/components/AlertFeed.tsx)
Real-time alert feed:
- WebSocket connection to `/ws/alerts`
- Live-updating table with latest detections
- Color-coded by attack type (red=DDoS, orange=Brute Force, yellow=SQL Injection, green=Benign)
- Auto-scroll to latest alerts
- Timestamp, source/destination IPs, attack type, confidence score

##### [NEW] [frontend/src/components/Dashboard.tsx](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/components/Dashboard.tsx)
Statistics dashboard:
- Real-time graphs using **Recharts** or **Chart.js**:
  - Attack type distribution (pie chart)
  - Detection timeline (line chart - attacks per minute)
  - Confidence score distribution (histogram)
- Total detections counter
- Attack breakdown by type
- Average confidence score

##### [NEW] [frontend/src/components/PcapUpload.tsx](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/components/PcapUpload.tsx)
PCAP file upload (secondary feature):
- Drag-and-drop file upload
- Progress indicator
- Results display after analysis

##### [NEW] [frontend/src/hooks/useWebSocket.ts](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/hooks/useWebSocket.ts)
Custom WebSocket hook:
- Manage WebSocket connection lifecycle
- Auto-reconnect on disconnect
- Type-safe message handling

##### [NEW] [frontend/src/services/api.ts](file:///d:/Uni/FYP/multivector_ml_ids/frontend/src/services/api.ts)
API client service:
- Axios-based HTTP client
- Type-safe API calls
- Error handling

##### [NEW] [frontend/tailwind.config.js](file:///d:/Uni/FYP/multivector_ml_ids/frontend/tailwind.config.js)
Tailwind CSS configuration:
- Custom color scheme for attack types
- Dark mode support
- Responsive breakpoints

---

### Component 7: Documentation & Attack Simulation

#### [NEW] [docs/attack_simulation.md](file:///d:/Uni/FYP/multivector_ml_ids/docs/attack_simulation.md)
Attack simulation documentation:
- **DDoS**: Using `hping3` or `slowloris` for SYN flood and slowloris attacks
- **Brute Force**: Using `hydra` or custom scripts for SSH/FTP brute force
- **SQL Injection**: Using `sqlmap` for automated SQL injection testing
- Command examples and expected PCAP outputs

#### [NEW] [docs/architecture.md](file:///d:/Uni/FYP/multivector_ml_ids/docs/architecture.md)
System architecture documentation:
- Component diagram
- Data flow diagram
- ML pipeline architecture
- API architecture

#### [NEW] [docs/limitations_future_work.md](file:///d:/Uni/FYP/multivector_ml_ids/docs/limitations_future_work.md)
Academic discussion:
- Current limitations (PCAP-only, 4 classes, single model)
- Future enhancements (deep learning, live capture, more attack types)
- Scalability considerations

---

### Component 8: Utility Scripts

#### [NEW] [scripts/train_pipeline.py](file:///d:/Uni/FYP/multivector_ml_ids/scripts/train_pipeline.py)
End-to-end training script:
- Execute full pipeline from data loading to model evaluation
- Single command execution for reproducibility

#### [NEW] [scripts/run_dashboard.py](file:///d:/Uni/FYP/multivector_ml_ids/scripts/run_dashboard.py)
Dashboard launcher script

---

## Verification Plan

### Automated Tests

1. **Dataset Verification**
   ```bash
   python scripts/verify_dataset.py
   ```
   - Verify all 8 Parquet files exist in `cicids2017/` directory
   - Load and validate 4 required files (Benign, Bruteforce, DDoS, WebAttacks)
   - Confirm 4 classes are properly labeled
   - Check for missing values and duplicates
   - Display samples per class and feature count

2. **Model Training**
   ```bash
   python scripts/train_pipeline.py
   ```
   - Execute full training pipeline
   - Verify model achieves ≥95% accuracy
   - Confirm model file is saved

3. **Evaluation Metrics**
   ```bash
   python src/evaluation/evaluator.py
   ```
   - Generate evaluation report
   - Verify all metrics (accuracy, precision, recall, F1)
   - Confirm confusion matrix generation

4. **Live Capture Test** (PRIMARY - requires admin privileges)
   ```bash
   # Run as Administrator
   python scripts/test_live_capture.py --interface "Ethernet"
   ```
   - List available network interfaces
   - Start live packet capture
   - Verify feature extraction from live traffic
   - Confirm real-time prediction output
   - Test capture start/stop functionality

5. **PCAP Inference Test** (SECONDARY)
   ```bash
   python scripts/test_inference.py --pcap data/sample_pcaps/ddos_sample.pcap
   ```
   - Test PCAP parsing with Scapy and pyshark
   - Verify feature extraction matches live capture
   - Confirm batch prediction output format

6. **Backend API Testing**
   ```bash
   # Run as Administrator (for live capture)
   python src/api/main.py
   ```
   - Start FastAPI server on `http://localhost:8000`
   - Test REST endpoints using `curl` or Postman:
     - `GET /api/interfaces`
     - `POST /api/capture/start`
     - `GET /api/alerts`
     - `GET /api/stats`
   - Test WebSocket connection to `/ws/alerts`
   - Verify real-time alert broadcasting

7. **Frontend Build & Integration**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Verify React app starts on `http://localhost:5173`
   - Test WebSocket connection to backend
   - Verify real-time alert updates
   - Test all UI components

### Manual Verification

1. **Live Capture Dashboard Testing** (PRIMARY)
   - Navigate to React frontend at `http://localhost:5173`
   - Select network interface from dropdown
   - Click "Start Capture" button (requires backend running as admin)
   - Verify real-time alerts appear in feed as traffic flows
   - Confirm WebSocket connection status indicator shows "Connected"
   - Generate test traffic (browse websites, ping) and verify detections
   - Check real-time graphs update (attack distribution, timeline)
   - Verify color-coding by attack type
   - Test "Stop Capture" functionality
   - Export alerts to CSV and verify file contents

2. **PCAP Upload Testing** (SECONDARY)
   - Upload sample PCAP files via UI
   - Verify batch analysis results display
   - Confirm predictions match expected attack types

3. **Thesis Documentation Review**
   - Review `results/evaluation_report.json` for thesis tables
   - Verify confusion matrix visualization quality
   - Confirm architecture diagrams are clear
   - Review limitations and future work section

4. **Windows Execution Validation**
   - Follow README installation steps on clean Windows environment
   - Install Npcap driver (WinPcap successor)
   - Verify Python and Node.js dependencies install correctly
   - Run backend as Administrator (required for live capture)
   - Test complete workflow from installation to live capture dashboard
   - Verify React frontend builds and connects to backend

---

## Expected Outcomes

- **Accuracy**: ≥95% on CICIDS2017 test set
- **Model Size**: ~50-200 MB (Random Forest with tuned parameters)
- **Live Capture Performance**: 
  - Real-time packet processing: 100-1000 packets/second
  - Feature extraction latency: <100ms per flow
  - Prediction latency: <50ms per flow
  - WebSocket alert delivery: <10ms
- **Dashboard**: 
  - React frontend at `http://localhost:5173`
  - FastAPI backend at `http://localhost:8000`
  - Real-time WebSocket alerts with <100ms latency
  - Interactive graphs and visualizations
- **Data Management**:
  - In-memory storage for last 1000 alerts
  - CSV export for historical analysis
  - No database complexity
- **Documentation**: Viva-defensible, thesis-ready materials with architecture diagrams
