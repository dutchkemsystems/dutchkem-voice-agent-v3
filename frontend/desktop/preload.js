const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  // App info
  getAppVersion: () => ipcRenderer.invoke("get-app-version"),
  getPlatform: () => ipcRenderer.invoke("get-platform"),

  // Interview control
  startInterview: () => ipcRenderer.invoke("start-interview"),
  stopInterview: () => ipcRenderer.invoke("stop-interview"),

  // Monitoring status
  getAudioStatus: () => ipcRenderer.invoke("get-audio-status"),
  getVideoStatus: () => ipcRenderer.invoke("get-video-status"),

  // Auto-start
  toggleAutoStart: () => ipcRenderer.invoke("toggle-auto-start"),
  getAutoStartStatus: () => ipcRenderer.invoke("get-auto-start-status"),

  // Desktop capture
  getDesktopCapturerSources: () =>
    ipcRenderer.invoke("desktop-capturer-sources"),

  // Notifications
  sendNotification: (title, body) =>
    ipcRenderer.invoke("send-notification", { title, body }),

  // Event listeners (with cleanup support)
  onNotification: (callback) => {
    const listener = (event, data) => callback(data);
    ipcRenderer.on("notification", listener);
    return () => ipcRenderer.removeListener("notification", listener);
  },

  onInterviewEvent: (callback) => {
    const listener = (event, data) => callback(data);
    ipcRenderer.on("interview-event", listener);
    return () => ipcRenderer.removeListener("interview-event", listener);
  },

  onAutoStartStatusChanged: (callback) => {
    const listener = (event, data) => callback(data);
    ipcRenderer.on("auto-start-status-changed", listener);
    return () =>
      ipcRenderer.removeListener("auto-start-status-changed", listener);
  },
});
