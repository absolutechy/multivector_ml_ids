"""
Capture Control Routes
API endpoints for controlling live capture and PCAP analysis.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import shutil

from src.capture.live_capture import LiveCapture
from src.capture.pcap_parser import PcapParser
from src.api.services.live_detection_service import LiveDetectionService
from config.config import BASE_DIR

router = APIRouter(prefix="/api/capture", tags=["capture"])

# Global live detection service
live_service = LiveDetectionService()


class CaptureStartRequest(BaseModel):
    """Request model for starting capture."""
    interface_name: Optional[str] = None
    interface_index: Optional[int] = None
    filter_str: Optional[str] = None
    duration: int = 0
    packet_count: int = 0


@router.get("/interfaces")
async def list_interfaces():
    """List available network interfaces."""
    try:
        interfaces = LiveCapture.list_interfaces()
        return {
            "count": len(interfaces),
            "interfaces": [
                {"index": i+1, "name": iface}
                for i, iface in enumerate(interfaces)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_capture(request: CaptureStartRequest):
    """Start live packet capture with detection."""
    try:
        success = live_service.start(
            interface_name=request.interface_name,
            interface_index=request.interface_index
        )
        
        if success:
            return {
                "message": "Live capture started successfully",
                "status": live_service.get_status()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start capture")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_capture():
    """Stop live packet capture."""
    try:
        live_service.stop()
        return {
            "message": "Capture stopped successfully",
            "status": live_service.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_capture_status():
    """Get current capture status."""
    return live_service.get_status()


@router.post("/pcap/upload")
async def upload_pcap(file: UploadFile = File(...)):
    """
    Upload and analyze PCAP file.
    
    Args:
        file: PCAP file to analyze
    """
    try:
        # Save uploaded file
        upload_dir = BASE_DIR / "data" / "sample_pcaps"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse PCAP
        parser = PcapParser(file_path)
        parser.parse_pcap()
        
        # Get summary
        summary = parser.get_flow_summary()
        
        return {
            "message": "PCAP uploaded and parsed successfully",
            "file_path": str(file_path),
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pcap/analyze/{filename}")
async def analyze_pcap(filename: str):
    """
    Analyze existing PCAP file.
    
    Args:
        filename: Name of PCAP file in data/sample_pcaps/
    """
    try:
        file_path = BASE_DIR / "data" / "sample_pcaps" / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PCAP file not found")
        
        # Parse PCAP
        parser = PcapParser(file_path)
        parser.parse_pcap()
        
        # Get summary
        summary = parser.get_flow_summary()
        
        return {
            "message": "PCAP analyzed successfully",
            "file_path": str(file_path),
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
