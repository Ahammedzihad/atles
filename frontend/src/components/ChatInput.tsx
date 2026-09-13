"use client";

import React, { useState, useRef, useEffect } from "react";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
}) => {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  // Auto-resize textarea height based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    const nextHeight = Math.min(textarea.scrollHeight, 160);
    textarea.style.height = `${Math.max(nextHeight, 24)}px`;
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed);
    setText("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send message on Enter without Shift, respecting IME composition
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      // Block submission if typing with Input Method Editor (IME)
      if (e.nativeEvent.isComposing || (e as unknown as { keyCode?: number }).keyCode === 229) {
        return;
      }

      formRef.current?.requestSubmit();
    }
  };

  const isSendDisabled = !text.trim() || isLoading;

  return (
    <div className={styles.inputContainer}>
      <form
        ref={formRef}
        onSubmit={handleSubmit}
        className={styles.inputForm}
        id="atles-chat-form"
      >
        <label htmlFor="atles-chat-input" className={styles.visuallyHidden}>
          Message Atles
        </label>

        <div className={styles.inputBox}>
          <textarea
            ref={textareaRef}
            id="atles-chat-input"
            className={styles.textarea}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isLoading
                ? "Atles is responding..."
                : "Ask Atles anything... (Press Enter to send)"
            }
            rows={1}
            disabled={isLoading}
          />

          <button
            type="submit"
            className={styles.sendButton}
            disabled={isSendDisabled}
            aria-label="Send message to Atles"
            title={isSendDisabled ? "Type a message to send" : "Send message"}
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>

        <div className={styles.footerRow}>
          <div className={styles.shortcutHint}>
            <span>Use</span>
            <kbd className={styles.kbd}>Enter ↵</kbd>
            <span>to send,</span>
            <kbd className={styles.kbd}>Shift + Enter</kbd>
            <span>for newline</span>
          </div>
          <span>Day 1 • Step 3 Prototype</span>
        </div>
      </form>
    </div>
  );
};
