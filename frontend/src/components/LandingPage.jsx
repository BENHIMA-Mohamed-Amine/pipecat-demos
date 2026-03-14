const steps = [
    { number: "01", title: "Start", desc: "Click the mic button bottom-right to initialize." },
    { number: "02", title: "Connect", desc: 'Wait for "Connected" status — then the bot is ready.' },
    { number: "03", title: "Speak", desc: "Just talk. Voice detection handles the rest — no button needed." },
    { number: "04", title: "Interrupt", desc: "Cut the bot off anytime, mid-sentence. It will stop and listen." },
    { number: "05", title: "Mute", desc: "Press the mic button inside the widget to mute / unmute." },
    { number: "06", title: "End", desc: 'Press "End call" or refresh to finish. Allow mic access when asked.' },
];

const contacts = [
    {
        label: "Email",
        href: "mailto:benhima.mohamed.amine@gmail.com",
        icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z" /></svg>,
    },
    {
        label: "LinkedIn",
        href: "https://www.linkedin.com/in/mohamed-amine-benhima/",
        icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" /></svg>,
    },
];

const styles = `
    .landing-root {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 80px;
        box-sizing: border-box;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #B4B2A9;
    }
    .landing-inner {
        width: 100%;
        max-width: 860px;
        display: flex;
        flex-direction: column;
    }
    .landing-title {
        font-size: 54px;
        font-weight: 600;
        line-height: 1.15;
        color: #E8E6E0;
        margin: 0 0 14px;
        letter-spacing: -0.02em;
        white-space: nowrap;
    }
    .landing-subtitle {
        font-size: 20px;
        line-height: 1.6;
        color: #888780;
        margin: 0;
    }
    .step-title { font-size: 20px; color: #C8C6BF; font-weight: 500; }
    .step-desc  { font-size: 20px; color: #888780; }
    .tip-text   { font-size: 17px; color: #7F77DD; }
    .footer-text { font-size: 16px; color: #5F5E5A; }
    .footer-link { font-size: 16px; }

    @media (max-width: 768px) {
        .landing-root { padding: 32px 24px; align-items: flex-start; }
        .landing-title { font-size: 32px; white-space: normal; }
        .landing-subtitle { font-size: 16px; }
        .step-title { font-size: 16px; }
        .step-desc  { font-size: 16px; }
        .tip-text   { font-size: 14px; }
        .footer-text { font-size: 13px; }
        .footer-link { font-size: 13px; }
        .footer-inner { flex-direction: column; gap: 10px; }
    }
`;

export function LandingPage() {
    return (
        <>
            <style>{styles}</style>
            <div className="landing-root">
                <div className="landing-inner">

                    {/* Header */}
                    <div style={{ marginBottom: 28 }}>
                        <div style={{
                            display: "inline-flex", alignItems: "center", gap: 8,
                            background: "#1C1C1A", border: "0.5px solid #2e2e2b",
                            borderRadius: 100, padding: "6px 16px", marginBottom: 18,
                        }}>
                            <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#7F77DD" }} />
                            <span style={{ fontSize: 13, color: "#888780", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                                Voice AI Demo
                            </span>
                        </div>

                        <h1 className="landing-title">
                            Talk to an AI,{" "}
                            <span style={{ color: "#7F77DD" }}>like a human.</span>
                        </h1>

                        <p className="landing-subtitle">
                            Real-time voice agent powered by Pipecat. No push-to-talk — just speak naturally. Works like ChatGPT Voice Mode.
                        </p>
                    </div>

                    {/* Divider + label */}
                    <div style={{ borderTop: "0.5px solid #2e2e2b", marginBottom: 18 }} />
                    <span style={{ fontSize: 13, letterSpacing: "0.1em", textTransform: "uppercase", color: "#5F5E5A", marginBottom: 16, display: "block" }}>
                        How it works
                    </span>

                    {/* Steps */}
                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        {steps.map((step, i) => (
                            <div key={i} style={{ display: "flex", gap: 20, alignItems: "baseline" }}>
                                <span style={{ fontSize: 12, color: "#3a3a36", fontFamily: "monospace", minWidth: 26 }}>
                                    {step.number}
                                </span>
                                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "baseline" }}>
                                    <span className="step-title">{step.title} —</span>
                                    <span className="step-desc">{step.desc}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Tip */}
                    <div style={{
                        margin: "22px 0",
                        background: "#1C1C1A",
                        border: "0.5px solid #2e2e2b",
                        borderLeft: "2px solid #7F77DD",
                        borderRadius: "0 6px 6px 0",
                        padding: "12px 20px",
                    }}>
                        <span style={{ fontSize: 15, color: "#7F77DD" }}>
                            💡 Tip — use the mic button inside the widget to mute yourself anytime. The bot will stop listening until you unmute. works great in noisy environnement
                        </span>
                    </div>

                    {/* Footer */}
                    <div className="footer-inner" style={{
                        borderTop: "0.5px solid #2e2e2b",
                        paddingTop: 16,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        flexWrap: "wrap",
                        gap: 12,
                    }}>
                        <span className="footer-text">
                            Made with <span style={{ color: "#E24B4A" }}>♥</span> by{" "}
                            <span style={{ color: "#888780" }}>BENHIMA Mohamed-amine</span>
                        </span>
                        <div style={{ display: "flex", gap: 20 }}>
                            {contacts.map((c) => (
                                <a key={c.label} href={c.href} target="_blank" rel="noreferrer"
                                    className="footer-link"
                                    style={{ display: "flex", alignItems: "center", gap: 6, color: "#5F5E5A", textDecoration: "none", transition: "color 0.2s" }}
                                    onMouseEnter={e => e.currentTarget.style.color = "#B4B2A9"}
                                    onMouseLeave={e => e.currentTarget.style.color = "#5F5E5A"}
                                >
                                    {c.icon}{c.label}
                                </a>
                            ))}
                        </div>
                    </div>

                </div>
            </div>
        </>
    );
}