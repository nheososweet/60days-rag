/**
 * Main Chat Page
 *
 * Features:
 * - Real-time streaming chat
 * - Auto-scroll to bottom
 * - Thinking mode support
 * - Settings panel
 * - Responsive design
 * - Dark theme
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { Trash2, Loader2, Bot } from "lucide-react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ChatMessage } from "@/components/chat/chat-message";
import { MessageInput } from "@/components/chat/message-input";
import { SettingsPanel } from "@/components/chat/settings-panel";
import { useChatStore } from "@/stores/chat-store";
import { streamChat } from "@/lib/api/qwen";
import type { ChatMessage as ChatMessageType } from "@/lib/api/qwen";

export default function ChatPage() {
  const {
    messages,
    addMessage,
    updateLastMessage,
    clearMessages,
    settings,
    isStreaming,
    setStreaming,
    setError,
  } = useChatStore();

  const scrollRef = useRef<HTMLDivElement>(null);
  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const [isThinkingStreaming, setIsThinkingStreaming] = useState(false);
  const [isContentStreaming, setIsContentStreaming] = useState(false);

  // Auto-scroll to bottom - instant during streaming for smoothness
  useEffect(() => {
    if (isAutoScroll && scrollRef.current) {
      // Use instant scroll during streaming to avoid janky smooth animations
      const behavior = isStreaming ? "instant" : "smooth";
      scrollRef.current.scrollIntoView({
        behavior: behavior as ScrollBehavior,
        block: "end",
      });
    }
  }, [messages, isAutoScroll, isStreaming]);

  // Handle sending message
  const handleSend = async (message: string) => {
    // Add user message
    const userMessage: ChatMessageType = {
      id: `user-${Date.now()}`,
      role: "user",
      content: message,
      timestamp: new Date(),
    };
    addMessage(userMessage);

    // Add assistant message placeholder immediately (no flash!)
    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage: ChatMessageType = {
      id: assistantId,
      role: "assistant",
      content: "",
      thinking: "",
      timestamp: new Date(),
    };
    addMessage(assistantMessage);

    setStreaming(true);
    setError(null);
    setIsThinkingStreaming(false);
    setIsContentStreaming(false);

    // Local accumulator
    let accumulatedThinking = "";
    let accumulatedContent = "";

    try {
      // Stream response and update last message in-place
      for await (const chunk of streamChat(message, settings, (err) => {
        console.error("Stream error:", err);
        setError(err.message);
        setStreaming(false);
      })) {
        console.log("Received chunk:", chunk);

        if (chunk.type === "thinking" && chunk.thinking_content) {
          setIsThinkingStreaming(true);
          const fullThinking = chunk.thinking_content;

          // Fake streaming effect for thinking (since backend sends full content at once)
          // Split by sentences for natural streaming
          const sentences = fullThinking.match(/[^.!?]+[.!?]+/g) || [
            fullThinking,
          ];
          let currentText = "";

          for (const sentence of sentences) {
            currentText += sentence;
            accumulatedThinking = currentText;
            updateLastMessage({ thinking: accumulatedThinking });
            // Small delay between sentences for natural effect
            await new Promise((resolve) => setTimeout(resolve, 50));
          }

          // Ensure full content is saved
          accumulatedThinking = fullThinking;
          updateLastMessage({ thinking: accumulatedThinking });
        } else if (chunk.type === "content" && chunk.chunk) {
          setIsThinkingStreaming(false);
          setIsContentStreaming(true);
          accumulatedContent += chunk.chunk;
          // Update in-place - smooth!
          updateLastMessage({ content: accumulatedContent });
        } else if (chunk.type === "finish" || chunk.done) {
          setIsThinkingStreaming(false);
          setIsContentStreaming(false);
          // Final update (optional, already updated)
          updateLastMessage({
            content: accumulatedContent,
            thinking: accumulatedThinking,
          });
          break;
        } else if (chunk.type === "error") {
          console.error("Error chunk:", chunk);
          setError(chunk.chunk || "Unknown error");
          break;
        }
      }
    } catch (error) {
      console.error("Catch error:", error);
      setError(
        error instanceof Error ? error.message : "Failed to send message"
      );
    } finally {
      setStreaming(false);
      setIsThinkingStreaming(false);
      setIsContentStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="shrink-0 border-b bg-card/50 backdrop-blur supports-backdrop-filter:bg-card/50">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary text-primary-foreground font-bold text-lg">
              Q3
            </div>
            <div>
              <h1 className="text-lg font-semibold">Qwen3 RAG Chat</h1>
              <p className="text-xs text-muted-foreground">
                AI Assistant with Thinking Mode
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={clearMessages}
              disabled={messages.length === 0 || isStreaming}
              title="Clear chat history"
            >
              <Trash2 className="w-5 h-5" />
            </Button>
            <SettingsPanel />
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full px-4">
          <div className="container max-w-4xl mx-auto py-6 space-y-4">
            {messages.length === 0 && !isStreaming && (
              <div className="flex flex-col items-center justify-center h-full text-center py-20">
                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <span className="text-4xl">🤖</span>
                </div>
                <h2 className="text-2xl font-semibold mb-2">
                  Welcome to Qwen3 Chat
                </h2>
                <p className="text-muted-foreground max-w-md">
                  Start a conversation with AI. Enable thinking mode to see the
                  reasoning process!
                </p>
              </div>
            )}

            {messages.map((msg, index) => {
              const isLastMessage = index === messages.length - 1;
              const isStreamingThisMessage =
                isStreaming && isLastMessage && msg.role === "assistant";

              // Skip rendering empty assistant message during initial loading
              const isEmptyAndWaiting =
                isStreamingThisMessage &&
                !msg.content &&
                !msg.thinking &&
                !isThinkingStreaming &&
                !isContentStreaming;

              if (isEmptyAndWaiting) {
                return null; // Don't render, show loading indicator instead
              }

              return (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  isStreaming={isStreamingThisMessage}
                  isThinkingStreaming={
                    isStreamingThisMessage && isThinkingStreaming
                  }
                  isContentStreaming={
                    isStreamingThisMessage && isContentStreaming
                  }
                />
              );
            })}

            {/* Initial loading - waiting for first chunk */}
            {isStreaming &&
              !isThinkingStreaming &&
              !isContentStreaming &&
              messages[messages.length - 1]?.role === "assistant" &&
              !messages[messages.length - 1]?.content &&
              !messages[messages.length - 1]?.thinking && (
                <div className="flex gap-3 p-4 animate-in fade-in slide-in-from-bottom-2">
                  <div className="shrink-0 w-10 h-10 rounded-full bg-accent flex items-center justify-center shadow-lg ring-2 ring-offset-2 ring-offset-background ring-accent/20">
                    <Bot className="w-5 h-5 text-accent-foreground" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        Qwen3
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(), "HH:mm:ss")}
                      </span>
                    </div>
                    <Card className="p-4 border-2">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">
                          Waiting for AI response...
                        </span>
                      </div>
                    </Card>
                  </div>
                </div>
              )}

            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </div>

      <Separator />

      {/* Input Area */}
      <div className="shrink-0">
        <MessageInput onSend={handleSend} disabled={isStreaming} />
      </div>
    </div>
  );
}
