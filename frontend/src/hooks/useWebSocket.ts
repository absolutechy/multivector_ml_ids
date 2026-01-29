// Custom WebSocket Hook
import { useEffect, useRef, useState, useCallback } from 'react';
import type { Alert, Statistics } from '../services/api';

const WS_URL = 'ws://localhost:8000/ws';

interface WebSocketMessage {
    type: 'alert' | 'statistics' | 'status' | 'pong';
    data: any;
}

export const useWebSocket = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [latestAlert, setLatestAlert] = useState<Alert | null>(null);
    const [statistics, setStatistics] = useState<Statistics | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const connect = useCallback(() => {
        try {
            const ws = new WebSocket(WS_URL);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                try {
                    const message: WebSocketMessage = JSON.parse(event.data);

                    switch (message.type) {
                        case 'alert':
                            setLatestAlert(message.data);
                            break;
                        case 'statistics':
                            setStatistics(message.data);
                            break;
                        case 'status':
                            // Handle status updates if needed
                            break;
                        case 'pong':
                            // Handle pong response
                            break;
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);

                // Attempt to reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, 3000);
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Error creating WebSocket:', error);
        }
    }, []);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
    }, []);

    const sendMessage = useCallback((message: string) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(message);
        }
    }, []);

    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return {
        isConnected,
        latestAlert,
        statistics,
        sendMessage
    };
};
