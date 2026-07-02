import { StrictMode, useEffect } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles/global.css";
import { eventClient } from "./api/eventClient";
import { useCompanyStore } from "./store/companyStore";

function Bootstrap() {
  const applySnapshot = useCompanyStore((s) => s.applySnapshot);
  const applyEvent = useCompanyStore((s) => s.applyEvent);
  const setConnected = useCompanyStore((s) => s.setConnected);

  useEffect(() => {
    const unsubSnap = eventClient.onSnapshot(applySnapshot);
    const unsubEvt = eventClient.onEvent(applyEvent);
    const unsubConn = eventClient.onConnection(setConnected);

    eventClient.connect();

    eventClient.fetchSnapshot().then(applySnapshot).catch(() => {
      // Bridge not running — WebSocket reconnect will handle it
    });

    return () => {
      unsubSnap();
      unsubEvt();
      unsubConn();
      eventClient.disconnect();
    };
  }, [applySnapshot, applyEvent, setConnected]);

  return <App />;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Bootstrap />
  </StrictMode>,
);
