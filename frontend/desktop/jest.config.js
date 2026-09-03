module.exports = {
  testEnvironment: "node",
  roots: ["<rootDir>/tests"],
  testMatch: ["**/*.test.js"],
  collectCoverageFrom: ["main.js", "preload.js"],
  coverageDirectory: "coverage",
  verbose: true,
};
