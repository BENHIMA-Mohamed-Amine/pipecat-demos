import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import { callbacks } from "./callbacks";

export const client = new PipecatClient({
    transport: new SmallWebRTCTransport(),
    enableMic: true,
    callbacks,
});