import { useState, useCallback, useRef, useEffect } from "react";
import { RTVIEvent } from "@pipecat-ai/client-js";
import { useRTVIClientEvent } from "@pipecat-ai/client-react";

const VISIBLE_COUNT = 4;

export function Transcript() {
    const [messages, setMessages] = useState([]);
    const bottomRef = useRef(null);

    useRTVIClientEvent(RTVIEvent.BotLlmText, useCallback((data) => {
        setMessages(prev => {
            const last = prev[prev.length - 1];
            if (last?.role === "bot") {
                return [...prev.slice(0, -1), { ...last, text: last.text + data.text }];
            }
            return [...prev, { id: Date.now(), role: "bot", text: data.text }];
        });
    }, []));

    useRTVIClientEvent(RTVIEvent.UserTranscript, useCallback((data) => {
        setMessages(prev => {
            const last = prev[prev.length - 1];
            if (last?.role === "user" && !last.final) {
                return [...prev.slice(0, -1), { ...last, text: data.text, final: data.final }];
            }
            return [...prev, { id: Date.now(), role: "user", text: data.text, final: data.final }];
        });
    }, []));

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const visible = messages.slice(-VISIBLE_COUNT);

    return (
        <div style={{ borderTop: "0.5px solid #2e2e2b", paddingTop: 16 }}>
            <div style={{
                position: "relative",
                display: "flex",
                flexDirection: "column",
                gap: 12,
                maskImage: "linear-gradient(to bottom, transparent 0%, black 30%)",
                WebkitMaskImage: "linear-gradient(to bottom, transparent 0%, black 30%)",
            }}>
                {visible.map((msg) => (
                    <div key={msg.id} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        <span style={{
                            fontSize: 12,
                            fontWeight: 500,
                            color: msg.role === "bot" ? "#7F77DD" : "#1D9E75",
                        }}>
                            {msg.role === "bot" ? "Assistant" : "You"}
                        </span>
                        <span style={{ fontSize: 15, color: "#888780", lineHeight: 1.5 }}>
                            {msg.text.trim()}
                        </span>
                    </div>
                ))}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}