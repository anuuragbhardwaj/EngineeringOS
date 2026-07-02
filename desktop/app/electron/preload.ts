import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("eosDesktop", {
  platform: process.platform,
  bridgeUrl: process.env.VITE_EOS_BRIDGE_HTTP ?? "http://127.0.0.1:9477",
  bridgeWs: process.env.VITE_EOS_BRIDGE_WS ?? "ws://127.0.0.1:9477/ws/events",
});
