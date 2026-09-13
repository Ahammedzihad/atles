"use client";

import React from "react";
import { ChatMessage } from "@/types/chat";
import styles from "./ChatMessageItem.module.css";

interface ChatMessageItemProps {
  message: ChatMessage;
}

/**
 * Lightweight helper to format basic markdown-like syntax (**bold**, `code`, newlines)
 * without pulling in heavy external dependencies.
 */
function renderFormattedContent(text: string) {
  const lines = text.split("\n");

  return lines.map((line, lineIdx) => {
    // Process **bold** and `code` inline
    const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g);

    return (
      <React.Fragment key={lineIdx}>
        {parts.map((part, partIdx) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return (
              <strong key={partIdx}>
                {part.slice(2, -2)}
              </strong>
            );
          }
          if (part.startsWith("`") && part.endsWith("`")) {
            return (
              <code key={partIdx}>
                {part.slice(1, -1)}
              </code>
            );
          }
          return <span key={partIdx}>{part}</span>;
        })}
        {lineIdx < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <div
      className={`${styles.messageRow} ${
        isUser ? styles.userRow : styles.assistantRow
      }`}
    >
      {!isUser && (
        <div className={`${styles.avatar} ${styles.atlesAvatar}`} aria-label="Atles Avatar">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ffffff"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2L2 19h20L12 2z" />
          </svg>
        </div>
      )}

      <div className={styles.contentWrapper}>
        <div
          className={`${styles.bubble} ${
            isUser ? styles.userBubble : styles.assistantBubble
          }`}
        >
          <div className={styles.formattedContent}>
            {renderFormattedContent(message.content)}
          </div>
        </div>
        <span className={styles.timestamp}>{message.timestamp}</span>
      </div>

      {isUser && (
        <div className={`${styles.avatar} ${styles.userAvatar}`} aria-label="User Avatar">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ffffff"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </div>
      )}
    </div>
  );
};
