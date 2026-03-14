import { usePipecatClientTransportState } from "@pipecat-ai/client-react";

const STATE_CONFIG = {
    disconnected: { label: "Disconnected", color: "#5F5E5A" },
    initializing: { label: "Initializing...", color: "#BA7517" },
    initialized: { label: "Devices ready", color: "#BA7517" },
    authenticating: { label: "Authenticating...", color: "#BA7517" },
    authenticated: { label: "Authenticated", color: "#BA7517" },
    connecting: { label: "Connecting...", color: "#BA7517" },
    connected: { label: "Waiting for bot...", color: "#BA7517" },  // not ready yet!
    ready: { label: "Connected", color: "#1D9E75" },           // ✅ only green here
    disconnecting: { label: "Disconnecting...", color: "#5F5E5A" },
    error: { label: "Error", color: "#E24B4A" },
};

export function StatusBadge() {
    const state = usePipecatClientTransportState();
    const { label, color } = STATE_CONFIG[state] ?? STATE_CONFIG.disconnected;

    return (
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
            <span style={{ fontSize: 15, color: "#888780" }}>{label}</span>
        </div>
    );
}