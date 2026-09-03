/**
 * Tests for Electron preload script.
 * Validates the context bridge API surface exposed to the renderer process.
 */

const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const path = require("path");
const fs = require("fs");

const preloadContent = fs.readFileSync(
  path.join(__dirname, "..", "preload.js"),
  "utf-8"
);

describe("Preload Script - Context Bridge", () => {
  it("uses contextBridge.exposeInMainWorld", () => {
    assert.ok(preloadContent.includes("contextBridge.exposeInMainWorld"));
  });

  it("exposes electronAPI to renderer", () => {
    assert.ok(preloadContent.includes("electronAPI"));
  });

  it("uses ipcRenderer", () => {
    assert.ok(preloadContent.includes("ipcRenderer"));
  });
});

describe("Preload Script - API Methods", () => {
  const requiredMethods = [
    "getAppVersion",
    "getPlatform",
    "startInterview",
    "stopInterview",
    "getAudioStatus",
    "getVideoStatus",
    "toggleAutoStart",
    "getAutoStartStatus",
    "onNotification",
    "onInterviewEvent",
    "getDesktopCapturerSources",
  ];

  requiredMethods.forEach((method) => {
    it(`exposes ${method}`, () => {
      assert.ok(
        preloadContent.includes(method),
        `preload.js should expose ${method}`
      );
    });
  });
});

describe("Preload Script - IPC Channel Usage", () => {
  it("uses ipcRenderer.invoke for request-response channels", () => {
    assert.ok(preloadContent.includes("ipcRenderer.invoke"));
  });

  it("uses ipcRenderer.on for event listeners", () => {
    assert.ok(preloadContent.includes("ipcRenderer.on"));
  });

  it("provides removeListener for cleanup", () => {
    assert.ok(preloadContent.includes("removeListener"));
  });

  it("channels use correct names", () => {
    const channels = [
      "get-app-version",
      "get-platform",
      "start-interview",
      "stop-interview",
      "get-audio-status",
      "get-video-status",
      "toggle-auto-start",
      "get-auto-start-status",
      "notification",
      "interview-event",
      "desktop-capturer-sources",
    ];

    channels.forEach((channel) => {
      assert.ok(
        preloadContent.includes(`"${channel}"`) || preloadContent.includes(`'${channel}'`),
        `preload.js should reference channel "${channel}"`
      );
    });
  });
});
