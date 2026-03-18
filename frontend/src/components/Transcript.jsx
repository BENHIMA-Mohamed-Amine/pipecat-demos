import { useState, useCallback, useRef, useEffect } from "react";
import { RTVIEvent } from "@pipecat-ai/client-js";
import { useRTVIClientEvent } from "@pipecat-ai/client-react";

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

    useRTVIClientEvent(RTVIEvent.ServerMessage, useCallback((data) => {
        if (data.event === "tool-call-start") {
            setMessages(prev => [
                ...prev,
                { id: `tool-${data.tool}-${Date.now()}`, role: "tool", tool: data.tool, status: "pending" },
            ]);
        } else if (data.event === "tool-call-result") {
            setMessages(prev =>
                prev.map(m =>
                    m.role === "tool" && m.status === "pending"
                        ? { ...m, status: "done" }
                        : m
                )
            );
        }
    }, []));

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div style={{ borderTop: "0.5px solid #2e2e2b", paddingTop: 16 }}>
            <div style={{
                height: 360,
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                gap: 12,
                paddingTop: 24,
                maskImage: "linear-gradient(to bottom, transparent 0%, black 10%)",
                WebkitMaskImage: "linear-gradient(to bottom, transparent 0%, black 10%)",
            }}>
                {messages.map((msg) => {
                    if (msg.role === "tool") {
                        const done = msg.status === "done";
                        return (
                            <div key={msg.id} style={{ display: "flex", flexDirection: "column", gap: 3, flexShrink: 0 }}>
                                <span style={{ fontSize: 11, fontWeight: 500, color: "#5F5E5A" }}>Tool</span>
                                <div style={{
                                    display: "inline-flex", alignItems: "center", gap: 8,
                                    background: "#1a1a18",
                                    border: "0.5px solid #2e2e2b",
                                    borderLeft: `2px solid ${done ? "#1D9E75" : "#534AB7"}`,
                                    borderRadius: "0 6px 6px 0",
                                    padding: "7px 12px",
                                    width: "fit-content",
                                    transition: "border-left-color 0.3s",
                                }}>
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill={done ? "#1D9E75" : "#7F77DD"}>
                                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                                    </svg>
                                    <span style={{ fontSize: 13, color: done ? "#1D9E75" : "#7F77DD", fontFamily: "monospace" }}>
                                        {msg.tool}
                                    </span>
                                    {done ? (
                                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#1D9E75" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                            <polyline points="20 6 9 17 4 12" />
                                        </svg>
                                    ) : (
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#534AB7" strokeWidth="2.5" strokeLinecap="round">
                                            <circle cx="12" cy="12" r="10" />
                                            <path d="M12 6v6l4 2" />
                                        </svg>
                                    )}
                                </div>
                            </div>
                        );
                    }

                    return (
                        <div key={msg.id} style={{ display: "flex", flexDirection: "column", gap: 4, flexShrink: 0 }}>
                            <span style={{
                                fontSize: 11,
                                fontWeight: 500,
                                color: msg.role === "bot" ? "#7F77DD" : "#1D9E75",
                            }}>
                                {msg.role === "bot" ? "Assistant" : "You"}
                            </span>
                            <span style={{ fontSize: 14, color: "#888780", lineHeight: 1.6, textAlign: "justify", display: "block" }}>
                                {msg.text.trim()}
                            </span>
                        </div>
                    );
                })}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}