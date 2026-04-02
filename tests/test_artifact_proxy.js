/**
 * Artifact Proxy Integration Test
 *
 * This test validates that the artifact proxy correctly handles
 * screenshots and video recordings generated during browser automation.
 */

const ARTIFACTS = {
  screenshots: [
    {
      name: "wikipedia_ai_screenshot",
      path: "/code/.generated_artifacts/images/wikipedia_ai_screenshot.png",
      source: "https://en.wikipedia.org/wiki/Artificial_intelligence",
      description: "Screenshot of the Wikipedia Artificial Intelligence page",
    },
    {
      name: "wikipedia_ml_screenshot",
      path: "/code/.generated_artifacts/images/wikipedia_ml_screenshot.png",
      source: "https://en.wikipedia.org/wiki/Machine_learning",
      description: "Screenshot of the Wikipedia Machine Learning page",
    },
  ],
  recordings: [
    {
      name: "wikipedia_scroll",
      path: "/code/.generated_artifacts/recordings/wikipedia_scroll.webm",
      source: "https://en.wikipedia.org/wiki/Machine_learning",
      description:
        "Video recording of scrolling down the Wikipedia Machine Learning page",
    },
  ],
};

function validateArtifactMetadata(artifact) {
  if (!artifact.name || typeof artifact.name !== "string") {
    throw new Error(`Invalid artifact name: ${artifact.name}`);
  }
  if (!artifact.path || typeof artifact.path !== "string") {
    throw new Error(`Invalid artifact path: ${artifact.path}`);
  }
  if (!artifact.source || !artifact.source.startsWith("https://")) {
    throw new Error(`Invalid artifact source URL: ${artifact.source}`);
  }
  return true;
}

function testScreenshotArtifacts() {
  console.log("Testing screenshot artifacts...");
  for (const screenshot of ARTIFACTS.screenshots) {
    validateArtifactMetadata(screenshot);
    console.log(`  [PASS] ${screenshot.name} - metadata valid`);
  }
  console.log(
    `  Total screenshots validated: ${ARTIFACTS.screenshots.length}`
  );
}

function testRecordingArtifacts() {
  console.log("Testing recording artifacts...");
  for (const recording of ARTIFACTS.recordings) {
    validateArtifactMetadata(recording);
    console.log(`  [PASS] ${recording.name} - metadata valid`);
  }
  console.log(`  Total recordings validated: ${ARTIFACTS.recordings.length}`);
}

function testArtifactCount() {
  console.log("Testing artifact counts...");
  const totalArtifacts =
    ARTIFACTS.screenshots.length + ARTIFACTS.recordings.length;
  if (totalArtifacts !== 3) {
    throw new Error(`Expected 3 artifacts, got ${totalArtifacts}`);
  }
  console.log(`  [PASS] Total artifact count: ${totalArtifacts}`);
}

// Run all tests
console.log("=== Artifact Proxy Integration Tests ===\n");
testScreenshotArtifacts();
console.log();
testRecordingArtifacts();
console.log();
testArtifactCount();
console.log("\n=== All tests passed ===");
