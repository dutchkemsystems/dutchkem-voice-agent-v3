/**
 * Tests for Electron main process functionality.
 * Validates the core main process logic using Node.js built-in test runner.
 */

const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const path = require("path");
const fs = require("fs");

const mainContent = fs.readFileSync(
  path.join(__dirname, "..", "main.js"),
  "utf-8"
);

describe("Electron Main Process - Window Configuration", () => {
  it("window dimensions are 1200x800", () => {
    const widthMatch = mainContent.match(/width:\s*(\d+)/);
    const heightMatch = mainContent.match(/height:\s*(\d+)/);
    assert.ok(widthMatch, "width config found");
    assert.ok(heightMatch, "height config found");
    assert.equal(widthMatch[1], "1200");
    assert.equal(heightMatch[1], "800");
  });

  it("context isolation is enabled", () => {
    assert.ok(mainContent.includes("contextIsolation: true"));
  });

  it("node integration is disabled", () => {
    assert.ok(mainContent.includes("nodeIntegration: false"));
  });

  it("preload path points to preload.js", () => {
    assert.ok(mainContent.includes("preload.js"));
  });
});

describe("Electron Main Process - System Tray", () => {
  it("imports Tray from electron", () => {
    assert.ok(mainContent.includes("Tray"));
  });

  it("has createTray function", () => {
    assert.ok(mainContent.includes("createTray"));
  });

  it("sets context menu on tray", () => {
    assert.ok(mainContent.includes("setContextMenu"));
  });

  it("sets tooltip on tray", () => {
    assert.ok(mainContent.includes("setToolTip"));
  });

  it("tray menu has Show item", () => {
    assert.ok(mainContent.includes("Show"), "tray menu should have Show");
  });

  it("tray menu has Start Interview item", () => {
    assert.ok(mainContent.includes("Start Interview"), "tray menu should have Start Interview");
  });

  it("tray menu has Quit item", () => {
    assert.ok(mainContent.includes("Quit"), "tray menu should have Quit");
  });

  it("tray menu has Enable/Disable Auto-Start item", () => {
    assert.ok(
      mainContent.includes("Enable Auto-Start") || mainContent.includes("Disable Auto-Start"),
      "tray menu should have auto-start toggle"
    );
  });
});

describe("Electron Main Process - Minimize to Tray", () => {
  it("handles close event to hide window", () => {
    assert.ok(mainContent.includes("mainWindow.hide()"));
  });

  it("uses isQuiting flag for quit behavior", () => {
    assert.ok(mainContent.includes("isQuiting"));
  });
});

describe("Electron Main Process - Auto-Start on Login", () => {
  it("uses setLoginItemSettings", () => {
    assert.ok(mainContent.includes("setLoginItemSettings"));
  });

  it("sets openAtLogin property", () => {
    assert.ok(mainContent.includes("openAtLogin"));
  });

  it("passes --hidden args for hidden start", () => {
    assert.ok(mainContent.includes("--hidden"));
  });
});

describe("Electron Main Process - Auto-Updater", () => {
  it("imports autoUpdater from electron-updater", () => {
    assert.ok(mainContent.includes("autoUpdater"));
    assert.ok(mainContent.includes("electron-updater"));
  });

  it("sets up update check", () => {
    assert.ok(
      mainContent.includes("checkForUpdates") ||
      mainContent.includes("autoUpdater.checkForUpdates") ||
      mainContent.includes("checkForUpdatesAndNotify")
    );
  });

  it("handles update events", () => {
    assert.ok(
      mainContent.includes("update-available") ||
      mainContent.includes("update-downloaded") ||
      mainContent.includes("checking-for-update")
    );
  });
});

describe("Electron Main Process - Background Monitoring", () => {
  it("imports desktopCapturer", () => {
    assert.ok(mainContent.includes("desktopCapturer"));
  });

  it("has startInterview function", () => {
    assert.ok(mainContent.includes("startInterview"));
  });

  it("has stopInterview function", () => {
    assert.ok(mainContent.includes("stopInterview"));
  });

  it("gets screen capture sources", () => {
    assert.ok(mainContent.includes("getSources"));
    assert.ok(mainContent.includes("screen"));
  });

  it("sends interview event to renderer", () => {
    assert.ok(mainContent.includes("webContents.send"));
  });
});

describe("Electron Main Process - IPC Handlers", () => {
  it("registers get-app-version handler", () => {
    assert.ok(mainContent.includes("get-app-version"));
  });

  it("registers get-platform handler", () => {
    assert.ok(mainContent.includes("get-platform"));
  });

  it("registers start-interview handler", () => {
    assert.ok(mainContent.includes("start-interview"));
  });

  it("registers stop-interview handler", () => {
    assert.ok(mainContent.includes("stop-interview"));
  });

  it("registers toggle-auto-start handler", () => {
    assert.ok(mainContent.includes("toggle-auto-start"));
  });

  it("registers get-auto-start-status handler", () => {
    assert.ok(mainContent.includes("get-auto-start-status"));
  });

  it("registers get-audio-status handler", () => {
    assert.ok(mainContent.includes("get-audio-status"));
  });

  it("registers get-video-status handler", () => {
    assert.ok(mainContent.includes("get-video-status"));
  });
});

describe("Electron Main Process - Notifications", () => {
  it("imports Notification from electron", () => {
    assert.ok(mainContent.includes("Notification"));
  });

  it("has sendNotification or notification creation logic", () => {
    assert.ok(
      mainContent.includes("sendNotification") ||
      mainContent.includes("new Notification") ||
      mainContent.includes("notification")
    );
  });
});

describe("Electron Main Process - Deep-link IPC Events", () => {
  it("sends notification to renderer via IPC", () => {
    assert.ok(mainContent.includes("notification"));
  });

  it("sends desktop-capturer-sources via IPC", () => {
    assert.ok(mainContent.includes("desktop-capturer-sources"));
  });
});
