export const callbacks = {
    onConnected: () => console.log("✅ Connected"),
    onDisconnected: () => console.log("❌ Disconnected"),
    onBotReady: () => console.log("🤖 Bot ready"),
    onBotStartedSpeaking: () => console.log("🔊 Bot started speaking"),
    onBotStoppedSpeaking: () => console.log("🔇 Bot stopped speaking"),
    onUserStartedSpeaking: () => console.log("🎙️ User started speaking"),
    onUserStoppedSpeaking: () => console.log("🎙️ User stopped speaking"),
    // onUserTranscript: (data) => console.log("👤 User said:", data.text),
    // onBotOutput: (data) => {
    //     if (!data.spoken) console.log("🤖 Bot said:", data.text);
    // },
    onError: (error) => console.error("💥 Error:", error),
    onServerMessage: (data) => {
        if (data.event === "tool-call-start") {
            console.log("🔧 Tool call:", data.tool);
        } else if (data.event === "tool-call-result") {
            console.log("📦 Tool result:", data.content);
        }
    },
};