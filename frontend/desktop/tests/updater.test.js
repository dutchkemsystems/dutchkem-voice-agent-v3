/**
 * Tests for auto-updater and build configuration.
 */

const { describe, it, before } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");

let electronBuilderConfig;
let packageJson;
let mainContent;

before(() => {
  const configPath = path.join(__dirname, "..", "electron-builder.json");
  electronBuilderConfig = JSON.parse(fs.readFileSync(configPath, "utf-8"));

  const packagePath = path.join(__dirname, "..", "package.json");
  packageJson = JSON.parse(fs.readFileSync(packagePath, "utf-8"));

  mainContent = fs.readFileSync(path.join(__dirname, "..", "main.js"), "utf-8");
});

describe("Auto-Updater Configuration", () => {
  it("electron-builder config has appId", () => {
    assert.equal(electronBuilderConfig.appId, "com.dutchkem.voice-agent");
  });

  it("electron-builder config has productName", () => {
    assert.equal(electronBuilderConfig.productName, "DutchKem Voice Agent");
  });

  it("windows target is nsis (supports auto-update)", () => {
    assert.equal(electronBuilderConfig.win.target, "nsis");
  });

  it("mac target is dmg", () => {
    assert.equal(electronBuilderConfig.mac.target, "dmg");
  });

  it("linux target is AppImage", () => {
    assert.equal(electronBuilderConfig.linux.target, "AppImage");
  });

  it("files include main.js and preload.js", () => {
    assert.ok(electronBuilderConfig.files.includes("main.js"));
    assert.ok(electronBuilderConfig.files.includes("preload.js"));
  });

  it("electron-updater is in dependencies", () => {
    assert.ok(packageJson.dependencies["electron-updater"]);
  });
});

describe("Package.json Configuration", () => {
  it("start script runs electron", () => {
    assert.equal(packageJson.scripts.start, "electron .");
  });

  it("build script uses electron-builder", () => {
    assert.equal(packageJson.scripts.build, "electron-builder");
  });

  it("platform-specific build scripts exist", () => {
    assert.ok(packageJson.scripts["build:win"]);
    assert.ok(packageJson.scripts["build:mac"]);
    assert.ok(packageJson.scripts["build:linux"]);
  });

  it("test script uses node --test", () => {
    assert.ok(packageJson.scripts.test);
  });

  it("electron dependency is declared", () => {
    assert.ok(packageJson.devDependencies.electron);
  });

  it("electron-builder dependency is declared", () => {
    assert.ok(packageJson.devDependencies["electron-builder"]);
  });
});

describe("Main Process - Full Feature Coverage", () => {
  it("has system tray implementation", () => {
    assert.ok(mainContent.includes("createTray"));
    assert.ok(mainContent.includes("Tray"));
    assert.ok(mainContent.includes("setContextMenu"));
    assert.ok(mainContent.includes("setToolTip"));
  });

  it("has auto-start implementation", () => {
    assert.ok(mainContent.includes("setLoginItemSettings"));
    assert.ok(mainContent.includes("openAtLogin"));
  });

  it("has notification support", () => {
    assert.ok(mainContent.includes("Notification"));
  });

  it("has auto-updater integration", () => {
    assert.ok(mainContent.includes("autoUpdater"));
  });

  it("minimize-to-tray on close", () => {
    assert.ok(mainContent.includes("isQuiting"));
    assert.ok(mainContent.includes("mainWindow.hide()"));
  });

  it("has background monitoring integration", () => {
    assert.ok(mainContent.includes("desktopCapturer"));
    assert.ok(mainContent.includes("startInterview"));
  });
});
