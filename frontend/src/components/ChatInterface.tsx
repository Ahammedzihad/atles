"use client";

import React, { useState, useCallback } from "react";
import { ChatMessage } from "@/types/chat";
import { sendMockMessage } from "@/services/mockChatService";
import { Header } from "./Header";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { ErrorBanner } from "./ErrorBanner";
import styles from "./ChatInterface.module.css";

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "welcome-msg-1",
    role: "assistant",
    content:
      "Hello! I am **Atles**, your personal AI assistant.\n\n" +
      "We're currently in Day 1 development. I'm connected to a local mock engine and ready to chat. " +
      "Type a prompt below or ask for `help` to see what's planned!",
    timestamp: "Just now",
  },
];

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastPrompt, setLastPrompt] = useState<string | null>(null);

  const formatCurrentTime = () => {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      setError(null);
      setLastPrompt(content);

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: content.trim(),
        timestamp: formatCurrentTime(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const replyContent = await sendMockMessage(content);

        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: replyContent,
          timestamp: formatCurrentTime(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err: unknown) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "An unexpected error occurred while communicating with Atles.";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading]
  );

  const handleRetry = useCallback(() => {
    if (lastPrompt) {
      handleSendMessage(lastPrompt);
    }
  }, [lastPrompt, handleSendMessage]);

  const handleDismissError = useCallback(() => {
    setError(null);
  }, []);

  const handleClearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setLastPrompt(null);
  }, []);

  return (
    <div className={styles.layoutWrapper}>
      <Header
        onClearChat={handleClearChat}
        messageCount={messages.length}
      />

      <main className={styles.mainContent}>
        {error && (
          <ErrorBanner
            message={error}
            onRetry={lastPrompt ? handleRetry : undefined}
            onDismiss={handleDismissError}
          />
        )}

        <MessageList
          messages={messages}
          isLoading={isLoading}
          onSelectPrompt={handleSendMessage}
        />

        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
};
