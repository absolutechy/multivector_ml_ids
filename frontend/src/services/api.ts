// API Client Service
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Alert {
    id: number;
    timestamp: string;
    attack_type: string;
    confidence: number;
    flow_key: [string, string, number, number, number] | null;
    is_attack: boolean;
}

export interface Statistics {
    total_predictions: number;
    attack_distribution: {
        [key: string]: {
            count: number;
            percentage: number;
        };
    };
    detection_rate: number;
    uptime_seconds: number;
    alerts_in_memory: number;
}

export interface NetworkInterface {
    index: number;
    name: string;
}

export interface CaptureStatus {
    is_running: boolean;
    capture: {
        is_capturing: boolean;
        interface: string | null;
        total_packets: number;
        active_flows: number;
        completed_flows: number;
        queue_size: number;
    };
    statistics: Statistics;
    model_loaded: boolean;
}

export interface ModelInfo {
    loaded: boolean;
    model_type?: string;
    n_features_original?: number | string;
    n_features_pca?: number;
    attack_classes?: string[];
    model_path?: string;
}

class APIClient {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    // Health check
    async healthCheck() {
        const response = await axios.get(`${this.baseURL}/health`);
        return response.data;
    }

    // Model info
    async getModelInfo(): Promise<ModelInfo> {
        const response = await axios.get(`${this.baseURL}/api/model/info`);
        return response.data;
    }

    // Statistics
    async getStatistics(): Promise<Statistics> {
        const response = await axios.get(`${this.baseURL}/api/statistics`);
        return response.data;
    }

    async resetStatistics() {
        const response = await axios.post(`${this.baseURL}/api/statistics/reset`);
        return response.data;
    }

    // Alerts
    async getAlerts(limit: number = 100, attackType?: string): Promise<{ count: number; alerts: Alert[] }> {
        const params: any = { limit };
        if (attackType) params.attack_type = attackType;

        const response = await axios.get(`${this.baseURL}/api/alerts`, { params });
        return response.data;
    }

    async clearAlerts() {
        const response = await axios.post(`${this.baseURL}/api/alerts/clear`);
        return response.data;
    }

    // Export
    async exportCSV() {
        const response = await axios.get(`${this.baseURL}/api/export/csv`);
        return response.data;
    }

    // Capture control
    async listInterfaces(): Promise<{ count: number; interfaces: NetworkInterface[] }> {
        const response = await axios.get(`${this.baseURL}/api/capture/interfaces`);
        return response.data;
    }

    async startCapture(interfaceIndex?: number, interfaceName?: string) {
        const response = await axios.post(`${this.baseURL}/api/capture/start`, {
            interface_index: interfaceIndex,
            interface_name: interfaceName
        });
        return response.data;
    }

    async stopCapture() {
        const response = await axios.post(`${this.baseURL}/api/capture/stop`);
        return response.data;
    }

    async getCaptureStatus(): Promise<CaptureStatus> {
        const response = await axios.get(`${this.baseURL}/api/capture/status`);
        return response.data;
    }

    // PCAP upload
    async uploadPCAP(file: File) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${this.baseURL}/api/capture/pcap/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }
}

export const apiClient = new APIClient();
