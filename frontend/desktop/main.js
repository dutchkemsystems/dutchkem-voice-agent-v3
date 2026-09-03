const {
  app,
  BrowserWindow,
  Tray,
  Menu,
  ipcMain,
  desktopCapturer,
  Notification,
} = require("electron");
const path = require("path");

let mainWindow;
let tray;
let audioStatus = { active: false, sources: [] };
let videoStatus = { active: false, sources: [] };

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
    title: "DutchKem Voice Agent",
    icon: path.join(__dirname, "assets", "icon.png"),
  });

  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:3000");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "out", "index.html"));
  }

  mainWindow.on("close", (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, "assets", "icon.png"));

  const contextMenu = Menu.buildFromTemplate([
    { label: "Show", click: () => mainWindow.show() },
    { label: "Start Interview", click: () => startInterview() },
    {
      label: "Enable Auto-Start",
      click: () => toggleAutoStart(),
      type: "checkbox",
      checked: app.getLoginItemSettings().openAtLogin,
    },
    { type: "separator" },
    {
      label: "Quit",
      click: () => {
        app.isQuiting = true;
        app.quit();
      },
    },
  ]);

  tray.setToolTip("DutchKem Voice Agent");
  tray.setContextMenu(contextMenu);

  tray.on("double-click", () => {
    mainWindow.show();
  });
}

function toggleAutoStart() {
  const current = app.getLoginItemSettings();
  const newState = !current.openAtLogin;
  app.setLoginItemSettings({
    openAtLogin: newState,
    path: process.execPath,
    args: ["--hidden"],
  });
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("auto-start-status-changed", newState);
  }
  rebuildTrayMenu();
  return newState;
}

function rebuildTrayMenu() {
  if (!tray || tray.isDestroyed()) return;
  const isAutoStart = app.getLoginItemSettings().openAtLogin;
  const contextMenu = Menu.buildFromTemplate([
    { label: "Show", click: () => mainWindow.show() },
    { label: "Start Interview", click: () => startInterview() },
    {
      label: isAutoStart ? "Disable Auto-Start" : "Enable Auto-Start",
      click: () => toggleAutoStart(),
    },
    { type: "separator" },
    {
      label: "Quit",
      click: () => {
        app.isQuiting = true;
        app.quit();
      },
    },
  ]);
  tray.setContextMenu(contextMenu);
}

async function startInterview() {
  try {
    const sources = await desktopCapturer.getSources({
      types: ["screen", "window"],
    });
    audioStatus = { active: true, sources: sources.map((s) => s.id) };
    videoStatus = { active: true, sources: sources.map((s) => s.id) };

    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send("interview-event", {
        type: "started",
        sources: sources.map((s) => ({
          id: s.id,
          name: s.name,
          thumbnailDataURL: s.thumbnail.toDataURL(),
        })),
      });
      mainWindow.show();
    }
  } catch (err) {
    sendNotification("Interview Error", `Failed to start interview: ${err.message}`);
  }
}

function stopInterview() {
  audioStatus = { active: false, sources: [] };
  videoStatus = { active: false, sources: [] };
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("interview-event", { type: "stopped" });
  }
}

function sendNotification(title, body) {
  if (Notification.isSupported()) {
    const notification = new Notification({
      title,
      body,
      silent: false,
    });
    notification.show();
  }
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("notification", { title, body });
  }
}

function setupAutoUpdater() {
  try {
    const { autoUpdater } = require("electron-updater");
    autoUpdater.autoDownload = true;
    autoUpdater.autoInstallOnAppQuit = true;

    autoUpdater.on("checking-for-update", () => {
      sendNotification("Update", "Checking for updates...");
    });

    autoUpdater.on("update-available", (info) => {
      sendNotification(
        "Update Available",
        `Version ${info.version} is being downloaded.`
      );
    });

    autoUpdater.on("update-not-available", () => {});

    autoUpdater.on("error", (err) => {
      sendNotification("Update Error", `Update error: ${err.message}`);
    });

    autoUpdater.on("update-downloaded", (info) => {
      sendNotification(
        "Update Ready",
        `Version ${info.version} downloaded. Restart to update.`
      );
    });

    autoUpdater.checkForUpdatesAndNotify();
  } catch (err) {
    // electron-updater not available in dev mode
  }
}

// IPC Handlers
ipcMain.handle("get-app-version", () => {
  return app.getVersion();
});

ipcMain.handle("get-platform", () => {
  return process.platform;
});

ipcMain.handle("start-interview", async () => {
  await startInterview();
  return { success: true };
});

ipcMain.handle("stop-interview", () => {
  stopInterview();
  return { success: true };
});

ipcMain.handle("get-audio-status", () => {
  return audioStatus;
});

ipcMain.handle("get-video-status", () => {
  return videoStatus;
});

ipcMain.handle("toggle-auto-start", () => {
  return toggleAutoStart();
});

ipcMain.handle("get-auto-start-status", () => {
  return app.getLoginItemSettings().openAtLogin;
});

ipcMain.handle("desktop-capturer-sources", async () => {
  const sources = await desktopCapturer.getSources({
    types: ["screen", "window"],
  });
  return sources.map((s) => ({
    id: s.id,
    name: s.name,
    thumbnailDataURL: s.thumbnail.toDataURL(),
  }));
});

ipcMain.handle("send-notification", (event, { title, body }) => {
  sendNotification(title, body);
  return { success: true };
});

// App Lifecycle
app.whenReady().then(() => {
  createWindow();
  createTray();
  setupAutoUpdater();

  const hiddenArg = process.argv.includes("--hidden");
  if (!hiddenArg) {
    mainWindow.show();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Single instance lock
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}
