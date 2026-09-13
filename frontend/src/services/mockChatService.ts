
/**
 * Service to generate mock AI responses for Atles.
 * In future phases, this can be seamlessly swapped or pointed to the real backend API.
 */
export async function sendMockMessage(
  userPrompt: string
): Promise<string> {
  // Simulate network / AI processing latency
  await new Promise((resolve) => setTimeout(resolve, 800));

  const trimmed = userPrompt.trim().toLowerCase();

  // Explicit trigger to demonstrate the error state requirement
  if (trimmed === "/error" || trimmed === "simulate error" || trimmed === "test error") {
    throw new Error(
      "Simulated connection failure: Unable to reach Atles core service. Please retry."
    );
  }

  if (trimmed.includes("who are you") || trimmed.includes("what is atles")) {
    return (
      "I am **Atles**, your personal AI assistant. Right now, we're in early development (Day 1). " +
      "Eventually, I'll be augmented with deep memory, local/cloud LLM intelligence, voice interaction, " +
      "and system automation capabilities."
    );
  }

  if (trimmed.includes("hello") || trimmed.includes("hi") || trimmed.startsWith("hey")) {
    return (
      "Hello! I am online and ready to assist. What are you planning to work on today?"
    );
  }

  if (trimmed.includes("help") || trimmed.includes("features")) {
    return (
      "Here is what I can do currently:\n\n" +
      "• **Interactive Chat**: Responsive real-time conversation interface\n" +
      "• **Keyboard Shortcuts**: Press `Enter` to submit, `Shift+Enter` for multi-line\n" +
      "• **Error Simulation**: Type `/error` to test the recovery and retry mechanisms\n" +
      "• **Extensible Architecture**: Ready to link to the backend in subsequent steps"
    );
  }

  if (trimmed.includes("backend") || trimmed.includes("api")) {
    return (
      "The backend integration is slated for the upcoming steps. This frontend is currently operating " +
      "in standalone mock mode with zero external telemetry or secret leaks."
    );
  }

  // Fallback response echoing context
  return (
    `I received your message: "${userPrompt}".\n\n` +
    `As Atles evolves, I'll connect to our local AI engine to process complex tasks, manage files, and automate workflows.`
  );
}
