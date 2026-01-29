"""
FastAPI Main Application
Entry point for the IDS backend API with WebSocket support.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.config import API_HOST, API_PORT, CORS_ORIGINS
from src.api.websocket.alert_handler import manager
from src.api.services.data_manager import data_manager
from src.inference.predictor import Predictor
from src.api.routes import capture

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Vector IDS API",
    description="Real-time Intrusion Detection System with ML-based attack classification",
    version="1.0.0"
)

# Include routers
app.include_router(capture.router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor (will be loaded on startup)
predictor = Predictor()


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    try:
        predictor.load_model_and_transformers()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not load model: {e}")
        print("  Run training pipeline first: python scripts/train_pipeline.py")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Vector IDS API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_loaded,
        "websocket_connections": manager.get_connection_count()
    }


@app.get("/api/model/info")
async def get_model_info():
    """Get model information."""
    return predictor.get_model_info()


@app.get("/api/statistics")
async def get_statistics():
    """Get current statistics."""
    return data_manager.get_statistics()


@app.get("/api/alerts")
async def get_alerts(limit: int = 100, attack_type: str = None):
    """
    Get recent alerts.
    
    Args:
        limit: Maximum number of alerts to return
        attack_type: Filter by attack type (optional)
    """
    alerts = data_manager.get_recent_alerts(limit=limit, attack_type=attack_type)
    return {
        "count": len(alerts),
        "alerts": alerts
    }


@app.post("/api/alerts/clear")
async def clear_alerts():
    """Clear all alerts from memory."""
    data_manager.clear_alerts()
    return {"message": "Alerts cleared successfully"}


@app.post("/api/statistics/reset")
async def reset_statistics():
    """Reset statistics."""
    data_manager.reset_statistics()
    return {"message": "Statistics reset successfully"}


@app.get("/api/export/csv")
async def export_alerts_csv():
    """Export all alerts to CSV."""
    file_path = data_manager.export_all_alerts_to_csv()
    return {
        "message": "Alerts exported successfully",
        "file_path": file_path
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alerts.
    
    Clients connect to this endpoint to receive real-time alerts and updates.
    """
    await manager.connect(websocket)
    
    try:
        # Send initial statistics
        stats = data_manager.get_statistics()
        await manager.send_personal_message({
            'type': 'statistics',
            'data': stats
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Handle client messages (ping/pong, etc.)
            if data == "ping":
                await manager.send_personal_message({
                    'type': 'pong',
                    'data': {'message': 'pong'}
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


def main():
    """Run the FastAPI server."""
    print("="*60)
    print("Starting Multi-Vector IDS API Server")
    print("="*60)
    print(f"Host: {API_HOST}")
    print(f"Port: {API_PORT}")
    print(f"Docs: http://localhost:{API_PORT}/docs")
    print(f"WebSocket: ws://localhost:{API_PORT}/ws")
    print("="*60 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()
