import { usePipecatClient, usePipecatClientTransportState } from "@pipecat-ai/client-react";
import { StatusBadge } from "./StatusBadge";
import { AIOrb } from "./AIOrb";
import { Transcript } from "./Transcript";
import { MicButton } from "./MicButton";

const ENDPOINT = import.meta.env.VITE_API_ENDPOINT;

const styles = `
    .voice-widget-container {
        position: fixed;
        bottom: 28px;
        right: 28px;
        width: 520px;
    }
    .voice-fab {
        position: fixed;
        bottom: 28px;
        right: 28px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    @media (max-width: 560px) {
        .voice-widget-container {
            bottom: 0;
            right: 0;
            left: 0;
            width: 100%;
        }
        .voice-fab {
            bottom: 24px;
            right: 24px;
        }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50%       { transform: translateY(-10px); }
    }
    @keyframes breathe {
        0%, 100% { box-shadow: 0 0 0 0 rgba(127,119,221,0); }
        50%       { box-shadow: 0 0 28px 10px rgba(127,119,221,0.35); }
    }
    @keyframes shadow-fade {
        0%, 100% { transform: scaleX(1);   opacity: 0.3; }
        50%       { transform: scaleX(0.6); opacity: 0.1; }
    }

    .voice-fab-btn {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: #534AB7;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: float 3s ease-in-out infinite, breathe 3s ease-in-out infinite;
        transition: background 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
    }
    .voice-fab-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: transform 0.5s ease;
    }
    .voice-fab-wrapper:hover {
        transform: scale(1.18);
    }
    .voice-fab-wrapper:hover .voice-fab-btn {
        background: #6057C9;
    }
    .voice-fab-shadow {
        width: 36px;
        height: 7px;
        border-radius: 50%;
        background: #7F77DD;
        filter: blur(4px);
        animation: shadow-fade 3s ease-in-out infinite;
        margin-top: 8px;
        transition: all 0.5s ease;
    }
    .voice-fab-wrapper:hover .voice-fab-shadow {
        transform: scaleX(1.35);
        opacity: 0.5;
    }
`;

export function VoiceWidget() {
    const client = usePipecatClient();
    const transportState = usePipecatClientTransportState();

    const isConnected = transportState === "ready" || transportState === "connected";
    const isConnecting = ["initializing", "initialized", "authenticating", "authenticated", "connecting"].includes(transportState);

    const connect = async () => {
        await client.initDevices();
        await client.connect({ webrtcRequestParams: { endpoint: ENDPOINT } });
        client.enableMic(true);
    };

    if (!isConnected && !isConnecting) {
        return (
            <>
                <style>{styles}</style>
                <div className="voice-fab">
                    <div className="voice-fab-wrapper">
                        <button onClick={connect} className="voice-fab-btn">
                            <svg width="26" height="26" viewBox="0 0 24 24" fill="white">
                                <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm-1 13.93A7 7 0 0 1 5 8H3a9 9 0 0 0 8 8.94V20H8v2h8v-2h-3v-3.07A9 9 0 0 0 21 8h-2a7 7 0 0 1-6 6.93z" />
                            </svg>
                        </button>
                        <div className="voice-fab-shadow" />
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <style>{styles}</style>
            <div className="voice-widget-container">
                <div style={{
                    background: "#1C1C1A",
                    borderRadius: "clamp(0px, (100vw - 561px) * 9999, 20px) clamp(0px, (100vw - 561px) * 9999, 20px) clamp(0px, (100vw - 561px) * 9999, 20px) clamp(0px, (100vw - 561px) * 9999, 20px)",
                    border: "0.5px solid #2e2e2b",
                    overflow: "hidden",
                }}>
                    {/* Mobile drag handle */}
                    <div style={{ display: "flex", justifyContent: "center", padding: "12px 0 0" }}>
                        <div style={{ width: 36, height: 4, borderRadius: 2, background: "#3a3a36" }} />
                    </div>

                    <div style={{ padding: "28px 32px 22px", display: "flex", flexDirection: "column", gap: 26 }}>
                        <StatusBadge />
                        <AIOrb />
                        <div style={{ textAlign: "left" }}>
                            <Transcript />
                        </div>
                    </div>

                    <div style={{
                        background: "#141413", borderTop: "0.5px solid #2e2e2b",
                        padding: "18px 24px", display: "flex",
                        alignItems: "center", justifyContent: "space-between",
                    }}>
                        <MicButton />
                        <button
                            onClick={() => client.disconnect()}
                            style={{
                                background: "#3D1515", border: "0.5px solid #A32D2D",
                                borderRadius: 20, padding: "11px 22px", cursor: "pointer",
                                display: "flex", alignItems: "center", gap: 6,
                            }}
                        >
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="#E24B4A">
                                <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1-9.4 0-17-7.6-17-17 0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z" />
                            </svg>
                            <span style={{ fontSize: 15, color: "#E24B4A", fontWeight: 500 }}>End call</span>
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}