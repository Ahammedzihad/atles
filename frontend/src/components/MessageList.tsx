"use client";

import React, { useEffect, useRef } from "react";
import { ChatMessage } from "@/types/chat";
import { ChatMessageItem } from "./ChatMessageItem";
import { TypingIndicator } from "./TypingIndicator";
import styles from "./MessageList.module.css";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSelectPrompt: (prompt: string) => void;
}

const STARTER_PROMPTS = [
  "What is Atles and how does it work?",
  "Show me the key features planned for Atles",
  "Simulate error (to test error state recovery)",
];

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  onSelectPrompt,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom smoothly when new messages arrive or loading state changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className={styles.container}>
      {messages.length === 0 ? (
        <div className={styles.welcomeCard}>
          <div className={styles.heroIcon}>
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ffffff"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2L2 19h20L12 2z" />
              <circle cx="12" cy="13" r="3" fill="#ffffff" />
            </svg>
          </div>

          <h1 className={styles.welcomeTitle}>Welcome to Atles</h1>
          <p className={styles.welcomeDesc}>
            Your intelligent personal AI companion. This is the Day 1 prototype
            running in mock mode with zero external dependencies.
          </p>

          <span className={styles.suggestionsTitle}>Suggested Prompts</span>
          <div className={styles.suggestionsGrid}>
            {STARTER_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                className={styles.suggestionBtn}
                onClick={() => onSelectPrompt(prompt)}
              >
                <span>{prompt}</span>
                <span className={styles.arrowIcon}>→</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <ChatMessageItem key={msg.id} message={msg} />
          ))}

          {isLoading && <TypingIndicator />}
        </>
      )}

      <div ref={bottomRef} className={styles.scrollAnchor} />
    </div>
  );
};
