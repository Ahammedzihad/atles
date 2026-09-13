"use client";

import React from "react";
import styles from "./Header.module.css";

interface HeaderProps {
  onClearChat?: () => void;
  messageCount?: number;
}

export const Header: React.FC<HeaderProps> = ({ onClearChat, messageCount = 0 }) => {
  return (
    <header className={styles.header}>
      <div className={styles.brandGroup}>
        <div className={styles.logoIcon} aria-label="Atles Logo">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ color: "#ffffff" }}
          >
            {/* Clean futuristic core / delta glyph */}
            <path d="M12 2L2 19h20L12 2z" />
            <circle cx="12" cy="13" r="2.5" fill="#ffffff" />
          </svg>
        </div>
        <div className={styles.titleArea}>
          <div className={styles.titleRow}>
            <span className={styles.title}>Atles</span>
            <span className={styles.badge}>v0.1</span>
          </div>
          <span className={styles.subtitle}>Personal AI Assistant</span>
        </div>
      </div>

      <div className={styles.statusGroup}>
        <div className={styles.statusIndicator} title="Frontend connected to mock engine">
          <span className={styles.statusDot} />
          <span className={styles.statusText}>Mock Engine</span>
        </div>

        {messageCount > 0 && onClearChat && (
          <button
            type="button"
            className={styles.clearBtn}
            onClick={onClearChat}
            title="Reset conversation"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 6h18" />
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
            </svg>
            <span>Clear</span>
          </button>
        )}
      </div>
    </header>
  );
};
