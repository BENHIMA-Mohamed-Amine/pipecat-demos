import {
  PipecatClientProvider,
  PipecatClientAudio,
} from "@pipecat-ai/client-react";
import { client } from "./pipecat/client";
import { VoiceWidget } from "./components/VoiceWidget";
import { LandingPage } from "./components/LandingPage";

export default function App() {
  return (
    <PipecatClientProvider client={client}>
      <LandingPage />
      <VoiceWidget />
      <PipecatClientAudio />
    </PipecatClientProvider>
  );
}
