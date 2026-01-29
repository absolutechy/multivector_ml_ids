# Multi-Vector Attack Detection System

Implementation of Multi-Vector Attack Detection and Classification Using Machine Learning for Improved Network Security.

## 🎯 Project Overview

This system uses machine learning (Random Forest) to detect and classify network attacks in real-time. It analyzes live network traffic and identifies 4 types of attacks:

- **Benign** (Normal traffic)
- **DDoS** (Distributed Denial of Service)
- **Brute Force** (SSH/FTP authentication attacks)
- **Web Attack** (SQL Injection + XSS + Web Brute Force)

## 📊 Key Features

- ✅ **Real-time Detection**: Live network packet capture and analysis
- ✅ **High Accuracy**: Random Forest classifier with ≥95% target accuracy
- ✅ **CICIDS2017 Dataset**: Trained on 1.2M+ samples with 78 features
- ✅ **FastAPI Backend**: RESTful API with WebSocket support
- ✅ **React Dashboard**: Modern TypeScript + Tailwind CSS frontend with real-time graphs
- ✅ **WebSocket Alerts**: Live alert broadcasting to connected clients
- ✅ **Performance**: <100ms feature extraction, <50ms prediction latency
- ✅ **Windows Compatible**: Npcap driver support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Live Network Traffic                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Packet Capture (Scapy/pyshark)                  │
│  - Network interface selection                               │
│  - Flow aggregation (5-tuple)                                │
│  - Timeout handling                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Feature Extraction (78 features)                   │
│  - Packet statistics, IAT, TCP flags                         │
│  - Flow duration, bytes/sec                                  │
│  - CICIDS2017-compatible features                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Preprocessing (Min-Max + PCA)                        │
│  - Normalization (0-1 scaling)                               │
│  - PCA (95% variance retention)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Random Forest Classifier                            │
│  - Trained model (200 estimators)                            │
│  - 4-class prediction                                        │
│  - Confidence scores                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI + WebSocket                             │
│  - Real-time alert broadcasting                              │
│  - Statistics tracking                                       │
│  - CSV logging                                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           React Dashboard (TypeScript)                       │
│  - Live alerts feed                                          │
│  - Real-time graphs                                          │
│  - Statistics display                                        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
multivector_ml_ids/
├── cicids2017/                 # CICIDS2017 dataset (Parquet files)
├── config/
│   └── config.py               # Central configuration
├── src/
│   ├── data/
│   │   └── dataset_loader.py   # Dataset loading
│   ├── preprocessing/
│   │   ├── data_cleaner.py     # Data cleaning
│   │   └── feature_engineer.py # Feature engineering
│   ├── models/
│   │   └── random_forest_trainer.py  # RF training
│   ├── evaluation/
│   │   └── evaluator.py        # Model evaluation
│   ├── capture/
│   │   ├── live_capture.py     # Live packet capture
│   │   └── pcap_parser.py      # PCAP file analysis
│   ├── inference/
│   │   ├── feature_extractor.py  # Flow feature extraction
│   │   └── predictor.py        # Real-time prediction
│   └── api/
│       ├── main.py             # FastAPI app
│       ├── routes/
│       │   └── capture.py      # Capture control routes
│       ├── websocket/
│       │   └── alert_handler.py  # WebSocket manager
│       └── services/
│           ├── data_manager.py  # Alert management
│           └── live_detection_service.py  # Integrated service
├── frontend/                   # React TypeScript Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── StatisticsDashboard.tsx
│   │   │   ├── AlertFeed.tsx
│   │   │   └── LiveCaptureControl.tsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   └── train_pipeline.py       # End-to-end training
├── docs/
│   └── windows_execution_guide.md
├── models/                     # Saved models
├── results/                    # Evaluation results
├── exports/                    # CSV exports
├── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Npcap Driver** (for Windows live capture)
   - Download: https://npcap.com/
   - Install with "WinPcap API-compatible Mode" enabled
3. **Administrator Privileges** (for live capture)

### Installation

```bash
# 1. Clone repository
cd d:\Uni\FYP\multivector_ml_ids

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Training the Model

```bash
# Run end-to-end training pipeline
python scripts\train_pipeline.py
```

This will:
- Load CICIDS2017 dataset (1.2M samples)
- Clean and preprocess data
- Apply Min-Max scaling and PCA
- Train Random Forest classifier
- Evaluate and save model
- Generate confusion matrix and metrics

**Expected Output:**
- `models/random_forest_model.pkl` - Trained model
- `models/scaler.pkl` - Feature scaler
- `models/pca.pkl` - PCA transformer
- `results/evaluation_report.json` - Metrics
- `results/confusion_matrix.png` - Visualization

### Running the Complete System

**Step 1: Start the Backend API**
```bash
# In terminal 1
python src\api\main.py
```

**Step 2: Start the Frontend Dashboard**
```bash
# In terminal 2
cd frontend
npm run dev
```

**Step 3: Access the Dashboard**
- Open browser: http://localhost:5173
- API Docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws

**Step 4: Start Live Capture (Administrator)**
- Use the "Live Capture" tab in the dashboard
- Select network interface
- Click "Start Capture"
- Watch real-time alerts appear!

### Testing Live Capture

```bash
# List network interfaces
python src\capture\live_capture.py

# Start live detection (run as Administrator)
python src\api\services\live_detection_service.py
```

## 📡 API Endpoints

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/api/model/info` | Model information |
| GET | `/api/statistics` | Current statistics |
| GET | `/api/alerts` | Recent alerts |
| POST | `/api/alerts/clear` | Clear alerts |
| POST | `/api/statistics/reset` | Reset statistics |
| GET | `/api/export/csv` | Export alerts to CSV |
| GET | `/api/capture/interfaces` | List network interfaces |
| POST | `/api/capture/start` | Start live capture |
| POST | `/api/capture/stop` | Stop capture |
| GET | `/api/capture/status` | Capture status |
| POST | `/api/capture/pcap/upload` | Upload PCAP file |

### WebSocket

Connect to `ws://localhost:8000/ws` to receive real-time alerts:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'alert') {
    console.log('New alert:', data.data);
  } else if (data.type === 'statistics') {
    console.log('Statistics update:', data.data);
  }
};
```

## 📊 Dataset

**CICIDS2017** - Located in `cicids2017/` directory

| File | Attack Type | Samples |
|------|-------------|---------|
| `Benign-Monday-no-metadata.parquet` | Benign | 458,831 |
| `Bruteforce-Tuesday-no-metadata.parquet` | Brute Force | 389,714 |
| `DDoS-Friday-no-metadata.parquet` | DDoS | 221,264 |
| `WebAttacks-Thursday-no-metadata.parquet` | Web Attack | 155,820 |

**Total**: 1,225,650 samples, 78 features

## 🎯 Performance Metrics

### Target Metrics
- ✅ **Accuracy**: ≥95%
- ✅ **Live Capture**: 100-1000 packets/second
- ✅ **Feature Extraction**: <100ms per flow
- ✅ **Prediction Latency**: <50ms per flow
- ✅ **WebSocket Delivery**: <10ms

### Model Performance
(Run `python scripts/train_pipeline.py` to generate)

- Accuracy: **XX.XX%**
- Precision (Macro): **XX.XX%**
- Recall (Macro): **XX.XX%**
- F1-Score (Macro): **XX.XX%**

See `results/evaluation_report.json` for detailed metrics.

## 🛠️ Configuration

Edit `config/config.py` to customize:

```python
# Dataset paths
DATASET_DIR = BASE_DIR / "cicids2017"

# Model parameters
TRAIN_TEST_SPLIT_RATIO = 0.2
PCA_VARIANCE_THRESHOLD = 0.95

# Random Forest hyperparameters
RF_PARAM_GRID = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    # ...
}

# Live capture
FLOW_TIMEOUT = 120  # seconds
PACKET_BUFFER_SIZE = 10000

# API
API_HOST = "0.0.0.0"
API_PORT = 8000
```

## 📝 Usage Examples

### 1. Train Model

```bash
python scripts\train_pipeline.py
```

### 2. Start API Server

```bash
python src\api\main.py
```

### 3. Live Detection (Administrator)

```bash
# List interfaces
python -c "from src.capture.live_capture import LiveCapture; LiveCapture.list_interfaces()"

# Start detection on interface 1
python src\api\services\live_detection_service.py
```

### 4. Analyze PCAP File

```bash
python src\capture\pcap_parser.py data\sample_pcaps\traffic.pcap
```

### 5. Test Prediction

```python
from src.inference.predictor import Predictor

predictor = Predictor()
predictor.load_model_and_transformers()

# Dummy features
features = {f'feature_{i}': 0.5 for i in range(78)}

result = predictor.predict_flow(features)
print(f"Attack Type: {result['attack_type']}")
print(f"Confidence: {result['confidence']*100:.1f}%")
```

## 🔧 Troubleshooting

### Issue: "Npcap not found"
**Solution**: Install Npcap from https://npcap.com/ with WinPcap compatibility mode

### Issue: "Permission denied" during live capture
**Solution**: Run Python as Administrator

### Issue: "Model not found"
**Solution**: Run training pipeline first: `python scripts/train_pipeline.py`

### Issue: "No interfaces found"
**Solution**: 
1. Install Npcap
2. Run as Administrator
3. Restart computer after Npcap installation

## 📚 Documentation

- [Implementation Plan](implementation_plan.md) - Detailed implementation guide
- [Task Breakdown](task.md) - Development tasks
- [Walkthrough](walkthrough.md) - Progress summary

## 🎓 Academic Context

This project is a **Final Year Project (FYP)** for:
- **Title**: Implementation of Multi-Vector Attack Detection and Classification Using Machine Learning for Improved Network Security
- **Objective**: Build an end-to-end IDS with ≥95% accuracy
- **Key Deliverables**:
  - Trained ML model
  - Real-time detection system
  - Web dashboard
  - Thesis documentation

## 🔮 Future Work

- [ ] Support for additional attack types
- [ ] Deep learning models (LSTM, CNN)
- [ ] Distributed deployment
- [ ] Mobile app integration
- [ ] Advanced visualization
- [ ] Automated response system

## 📄 License

Academic project - All rights reserved

## 👤 Author

Final Year Project - 2026

---

**Note**: This system requires administrator privileges for live network capture on Windows. Ensure Npcap is properly installed before running live detection features.
