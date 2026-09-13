"use client";

import React from "react";
import styles from "./TypingIndicator.module.css";

export const TypingIndicator: React.FC = () => {
  return (
    <div className={styles.wrapper} aria-label="Atles is typing" role="status">
      <div className={styles.avatar}>
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

      <div className={styles.bubble}>
        <span className={styles.dot} />
        <span className={styles.dot} />
        <span className={styles.dot} />
        <span className={styles.label}>Atles is thinking...</span>
      </div>
    </div>
  );
};
