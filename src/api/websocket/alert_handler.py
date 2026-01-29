"""
WebSocket Alert Handler
Manages WebSocket connections and broadcasts real-time alerts.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio


class ConnectionManager:
    """Manage WebSocket connections for real-time alerts."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✓ New WebSocket connection. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"✓ WebSocket disconnected. Total: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_alert(self, alert: dict):
        """
        Broadcast alert to all connected clients.
        
        Args:
            alert: Alert dictionary with prediction information
        """
        message = {
            'type': 'alert',
            'data': alert
        }
        await self.broadcast(message)
    
    async def broadcast_statistics(self, stats: dict):
        """
        Broadcast statistics update to all connected clients.
        
        Args:
            stats: Statistics dictionary
        """
        message = {
            'type': 'statistics',
            'data': stats
        }
        await self.broadcast(message)
    
    async def broadcast_status(self, status: dict):
        """
        Broadcast system status to all connected clients.
        
        Args:
            status: Status dictionary
        """
        message = {
            'type': 'status',
            'data': status
        }
        await self.broadcast(message)
    
    def broadcast_alert_sync(self, alert: dict):
        """
        Thread-safe method to broadcast alert from synchronous code.
        Uses a queue to avoid creating new event loops.
        
        Args:
            alert: Alert dictionary with prediction information
        """
        # Only broadcast if there are active connections
        if not self.active_connections:
            return
        
        message = {
            'type': 'alert',
            'data': alert
        }
        
        # Create task in existing event loop if available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast(message))
            else:
                # No running loop, skip broadcast
                pass
        except RuntimeError:
            # No event loop in this thread, skip broadcast
            pass
    
    def get_connection_count(self):
        """Get number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
