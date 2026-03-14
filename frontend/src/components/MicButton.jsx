import { useState, useCallback } from "react";
import { RTVIEvent } from "@pipecat-ai/client-js";
import { useRTVIClientEvent, usePipecatClientMicControl } from "@pipecat-ai/client-react";

const BASE_HEIGHT = 4;
const MAX_HEIGHT = 24;
const BAR_COUNT = 7;

export function MicButton() {
    const { enableMic, isMicEnabled } = usePipecatClientMicControl();
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [bars, setBars] = useState(Array(BAR_COUNT).fill(BASE_HEIGHT));

    useRTVIClientEvent(RTVIEvent.UserStartedSpeaking, useCallback(() => setIsSpeaking(true), []));
    useRTVIClientEvent(RTVIEvent.UserStoppedSpeaking, useCallback(() => {
        setIsSpeaking(false);
        setBars(Array(BAR_COUNT).fill(BASE_HEIGHT));
    }, []));

    useRTVIClientEvent(RTVIEvent.LocalAudioLevel, useCallback((level) => {
        if (!isSpeaking) return;
        setBars(Array.from({ length: BAR_COUNT }, () =>
            BASE_HEIGHT + Math.random() * level * MAX_HEIGHT
        ));
    }, [isSpeaking]));

    const barColor = !isMicEnabled ? "#5F5E5A" : "#1D9E75";

    return (
        <div
            onClick={() => enableMic(!isMicEnabled)}
            style={{
                display: "flex", alignItems: "center", gap: 10,
                background: "#2a2a27", border: "0.5px solid #3a3a36",
                borderRadius: 24, padding: "11px 18px", cursor: "pointer",
            }}
        >
            <div style={{ display: "flex", alignItems: "center", gap: 3, height: 24 }}>
                {bars.map((h, i) => (
                    <div key={i} style={{
                        width: 3, borderRadius: 2,
                        height: isMicEnabled ? h : BASE_HEIGHT,
                        background: barColor,
                        transition: "height 0.08s ease, background 0.2s",
                    }} />
                ))}
            </div>
            <span style={{ fontSize: 14, color: isMicEnabled ? "#B4B2A9" : "#5F5E5A" }}>
                {isMicEnabled ? "Mic on" : "Muted"}
            </span>
        </div>
    );
}