import { useState, useCallback, useEffect } from "react";
import { RTVIEvent } from "@pipecat-ai/client-js";
import { useRTVIClientEvent, usePipecatClientTransportState } from "@pipecat-ai/client-react";

const DOT_COUNT = 5;
const MIN_H = 8;
const MAX_H = 28;

export function AIOrb() {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [heights, setHeights] = useState(Array(DOT_COUNT).fill(MIN_H));
    const transportState = usePipecatClientTransportState();
    const isSpeakingActive = isSpeaking && transportState === "ready";

    useRTVIClientEvent(RTVIEvent.BotStartedSpeaking, useCallback(() => setIsSpeaking(true), []));
    useRTVIClientEvent(RTVIEvent.BotStoppedSpeaking, useCallback(() => {
        setIsSpeaking(false);
        setHeights(Array(DOT_COUNT).fill(MIN_H));
    }, []));
    useRTVIClientEvent(RTVIEvent.Disconnected, useCallback(() => {
        setIsSpeaking(false);
        setHeights(Array(DOT_COUNT).fill(MIN_H));
    }, []));
    // NOTE: We originally tried to use RTVIEvent.RemoteAudioLevel to drive the
    // dot animation dynamically based on real bot audio levels. This works with
    // Daily transport but NOT with SmallWebRTCTransport — it never fires.
    //
    // We also tried the server-side approach: enabling bot_audio_level_enabled=True
    // in RTVIObserverParams on the Python backend. The backend correctly sends
    // { type: "bot-audio-level", data: { value: ... } } RTVI messages. However,
    // "bot-audio-level" is not listed in the JS client's RTVIMessageType enum,
    // so the client silently ignores it and no RTVIEvent is emitted.
    //
    // Workaround: use setInterval to animate the dots randomly while the bot is
    // speaking. Visually identical to audio-driven animation at this update rate.
    // If Pipecat adds "bot-audio-level" to RTVIEvent in a future release, replace
    // this with: useRTVIClientEvent(RTVIEvent.BotAudioLevel, (level) => { ... })
    useEffect(() => {
        if (!isSpeakingActive) return;
        const interval = setInterval(() => {
            setHeights(Array.from({ length: DOT_COUNT }, () =>
                MIN_H + Math.random() * (MAX_H - MIN_H)
            ));
        }, 120);
        return () => clearInterval(interval);
    }, [isSpeakingActive]);

    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, height: 32 }}>
                {heights.map((h, i) => (
                    <div key={i} style={{
                        width: 8,
                        height: h,
                        borderRadius: 4,
                        background: isSpeakingActive ? "#7F77DD" : "#3a3a36",
                        transition: "height 0.1s ease, background 0.3s",
                    }} />
                ))}
            </div>
            <span style={{ fontSize: 12, color: isSpeakingActive ? "#7F77DD" : "#5F5E5A" }}>
                assistant
            </span>
        </div>
    );
}