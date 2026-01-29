# Windows Execution Guide

## Prerequisites

### 1. Install Python 3.8+

Download from: https://www.python.org/downloads/

Ensure "Add Python to PATH" is checked during installation.

### 2. Install Npcap Driver

**Required for live network capture**

1. Download Npcap: https://npcap.com/#download
2. Run installer as Administrator
3. **Important**: Check "Install Npcap in WinPcap API-compatible Mode"
4. Complete installation
5. **Restart your computer**

### 3. Verify Npcap Installation

```powershell
# Run PowerShell as Administrator
Get-Service npcap
```

Should show service status as "Running".

## Installation Steps

### 1. Navigate to Project Directory

```powershell
cd d:\Uni\FYP\multivector_ml_ids
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
```

### 3. Activate Virtual Environment

```powershell
.\venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### 4. Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- pandas, numpy, pyarrow
- scikit-learn, imbalanced-learn
- scapy, pyshark
- fastapi, uvicorn, websockets
- matplotlib, seaborn
- joblib, pydantic

## Training the Model

### Run Training Pipeline

```powershell
python scripts\train_pipeline.py
```

**Expected Duration**: 10-30 minutes (depending on hardware)

**Output Files**:
- `models/random_forest_model.pkl`
- `models/scaler.pkl`
- `models/pca.pkl`
- `results/evaluation_report.json`
- `results/confusion_matrix.png`

## Running the API Server

### Start FastAPI Server

```powershell
python src\api\main.py
```

**Access**:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- WebSocket: ws://localhost:8000/ws

### Test API Endpoints

Open browser and navigate to http://localhost:8000/docs

Try these endpoints:
1. GET `/health` - Check server status
2. GET `/api/model/info` - View model information
3. GET `/api/statistics` - View statistics
4. GET `/api/capture/interfaces` - List network interfaces

## Live Network Capture

### ⚠️ IMPORTANT: Administrator Privileges Required

### 1. List Network Interfaces

```powershell
# Run PowerShell as Administrator
python -c "from src.capture.live_capture import LiveCapture; LiveCapture.list_interfaces()"
```

### 2. Start Live Detection

```powershell
# Run as Administrator
python src\api\services\live_detection_service.py
```

**What happens**:
1. Loads trained model
2. Selects network interface (default: first interface)
3. Starts capturing packets
4. Extracts features from flows
5. Makes real-time predictions
6. Broadcasts alerts via WebSocket
7. Logs to CSV files

### 3. Monitor Alerts

While live detection is running:

**Option 1**: Check API
```powershell
# In another terminal
curl http://localhost:8000/api/alerts
```

**Option 2**: Check CSV logs
```powershell
# View today's alerts
type exports\alerts_2026-01-29.csv
```

**Option 3**: WebSocket (requires frontend or WebSocket client)

## PCAP File Analysis

### Analyze Pre-Captured Traffic

```powershell
# Place PCAP file in data/sample_pcaps/
python src\capture\pcap_parser.py data\sample_pcaps\traffic.pcap
```

**Output**:
- Flow statistics
- CSV export with flow details

### Upload PCAP via API

```powershell
# Using curl (install from https://curl.se/windows/)
curl -X POST "http://localhost:8000/api/capture/pcap/upload" -F "file=@traffic.pcap"
```

## Testing Individual Components

### 1. Test Dataset Loader

```powershell
python src\data\dataset_loader.py
```

### 2. Test Data Cleaner

```powershell
python src\preprocessing\data_cleaner.py
```

### 3. Test Feature Engineer

```powershell
python src\preprocessing\feature_engineer.py
```

### 4. Test Predictor

```powershell
python src\inference\predictor.py
```

### 5. Test Live Capture (Administrator)

```powershell
python src\capture\live_capture.py
```

## Common Issues and Solutions

### Issue 1: "Npcap not found" or "No interfaces found"

**Solution**:
1. Verify Npcap is installed: `Get-Service npcap`
2. Reinstall Npcap with WinPcap compatibility mode
3. Restart computer
4. Run Python as Administrator

### Issue 2: "Permission denied" during capture

**Solution**:
- Right-click PowerShell → "Run as Administrator"
- Or: Right-click Python script → "Run as Administrator"

### Issue 3: "Model not found"

**Solution**:
```powershell
python scripts\train_pipeline.py
```

### Issue 4: Import errors

**Solution**:
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 5: "Port 8000 already in use"

**Solution**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in config/config.py
```

## Performance Optimization

### For Faster Training

Edit `scripts/train_pipeline.py`:

```python
# Line ~35: Reduce samples for faster training
cleaner.balance_classes(method='undersample', target_samples=50000)

# Line ~56: Disable hyperparameter tuning
trainer.train_model(X_train_pca, y_train, tune_hyperparameters=False)
```

### For Live Capture

Edit `config/config.py`:

```python
# Reduce buffer size for lower memory usage
PACKET_BUFFER_SIZE = 1000

# Reduce flow timeout for faster processing
FLOW_TIMEOUT = 60  # seconds
```

## Stopping Services

### Stop API Server
Press `Ctrl+C` in the terminal running the API

### Stop Live Detection
Press `Ctrl+C` in the terminal running live detection

### Deactivate Virtual Environment
```powershell
deactivate
```

## Directory Structure After Setup

```
multivector_ml_ids/
├── venv/                       # Virtual environment
├── cicids2017/                 # Dataset (Parquet files)
├── models/                     # Trained models
│   ├── random_forest_model.pkl
│   ├── scaler.pkl
│   └── pca.pkl
├── results/                    # Evaluation results
│   ├── evaluation_report.json
│   ├── confusion_matrix.png
│   └── confusion_matrix_normalized.png
├── exports/                    # CSV exports
│   └── alerts_YYYY-MM-DD.csv
└── data/
    └── sample_pcaps/           # Uploaded PCAP files
```

## Next Steps

1. ✅ Train model: `python scripts\train_pipeline.py`
2. ✅ Start API: `python src\api\main.py`
3. ✅ Test live capture (as Admin): `python src\api\services\live_detection_service.py`
4. 🔄 Build React frontend (Phase 6 - Frontend)
5. 📊 Generate thesis documentation

## Support

For issues:
1. Check this guide
2. Review error messages carefully
3. Ensure all prerequisites are installed
4. Run as Administrator for live capture
5. Check `exports/` directory for CSV logs

---

**Remember**: Live network capture requires:
- ✅ Npcap driver installed
- ✅ Administrator privileges
- ✅ Computer restart after Npcap installation
