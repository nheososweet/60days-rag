/**
 * ChatMessage Component
 *
 * Displays individual messages với:
 * - Role-based styling
 * - Markdown rendering
 * - Collapsible thinking content
 * - Loading indicators
 * - Timestamp
 * - Animations
 */

"use client";

import { memo, useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { format } from "date-fns";
import {
  User,
  Bot,
  Brain,
  ChevronDown,
  ChevronUp,
  Loader2,
  Sparkles,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import type { ChatMessage as ChatMessageType } from "@/lib/api/qwen";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
  isThinkingStreaming?: boolean;
  isContentStreaming?: boolean;
}

function ChatMessageComponent({
  message,
  isStreaming = false,
  isThinkingStreaming = false,
  isContentStreaming = false,
}: ChatMessageProps) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  // Auto-expand when streaming, otherwise collapsed
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(true);

  return (
    <div
      className={cn(
        "flex gap-4 p-4 chat-message-transition",
        !isStreaming && "animate-in fade-in slide-in-from-bottom-2",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {/* Message Container */}
      <div
        className={cn(
          "flex gap-3 max-w-[85%] md:max-w-[75%]",
          isUser && "flex-row-reverse"
        )}
      >
        {/* Avatar */}
        <div
          className={cn(
            "shrink-0 w-10 h-10 rounded-full flex items-center justify-center",
            "shadow-lg ring-2 ring-offset-2 ring-offset-background transition-all",
            isUser ? "bg-primary ring-primary/20" : "bg-accent ring-accent/20"
          )}
        >
          {isUser ? (
            <User className="w-5 h-5 text-primary-foreground" />
          ) : (
            <Bot className="w-5 h-5 text-accent-foreground" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-2">
          {/* Header */}
          <div
            className={cn("flex items-center gap-2", isUser && "justify-end")}
          >
            <Badge
              variant={isUser ? "default" : "secondary"}
              className="text-xs"
            >
              {isUser ? "You" : "Qwen3"}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {format(message.timestamp, "HH:mm:ss")}
            </span>
          </div>

          {/* Thinking Content - Collapsible, subtle design */}
          {message.thinking && isAssistant && (
            <Card className="border-dashed bg-muted/30 overflow-hidden transition-all">
              <Button
                variant="ghost"
                onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
                className="w-full justify-between p-2.5 h-auto hover:bg-muted/50 text-left"
              >
                <div className="flex items-center gap-2">
                  <Brain className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">
                    Reasoning Process
                  </span>
                  {isThinkingStreaming && (
                    <Badge
                      variant="outline"
                      className="text-[10px] gap-1 animate-pulse"
                    >
                      <Loader2 className="w-2.5 h-2.5 animate-spin" />
                      thinking...
                    </Badge>
                  )}
                </div>
                {isThinkingExpanded ? (
                  <ChevronUp className="w-3.5 h-3.5 text-muted-foreground" />
                ) : (
                  <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
                )}
              </Button>

              {isThinkingExpanded && (
                <>
                  <Separator className="bg-border" />
                  <div className="p-3 text-xs text-muted-foreground whitespace-pre-wrap leading-relaxed bg-muted/20 animate-in slide-in-from-top-2">
                    {message.thinking}
                  </div>
                </>
              )}
            </Card>
          )}

          {/* Main Content - Only show if there's content or streaming */}
          {(message.content || isContentStreaming) && (
            <Card
              className={cn(
                "shadow-md transition-all duration-200 relative",
                isUser
                  ? "bg-primary text-primary-foreground p-4"
                  : "bg-card border-2"
              )}
            >
              {/* Content area with loading state */}
              <div className={cn(!isUser && "p-4")}>
                {/* Streaming indicator inside content */}
                {isContentStreaming && isAssistant && (
                  <div className="flex items-center gap-2 mb-3 text-muted-foreground">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-xs">Generating response...</span>
                  </div>
                )}

                <div
                  className={cn(
                    "prose prose-sm dark:prose-invert max-w-none",
                    isUser && "prose-invert"
                  )}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Custom rendering cho các elements
                      code: ({
                        node,
                        inline,
                        className,
                        children,
                        ...props
                      }: any) => {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline ? (
                          <pre className="bg-muted/50 p-3 rounded-lg overflow-x-auto">
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        ) : (
                          <code
                            className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono"
                            {...props}
                          >
                            {children}
                          </code>
                        );
                      },
                      a: ({ node, children, ...props }: any) => (
                        <a
                          className="text-blue-500 hover:underline"
                          target="_blank"
                          rel="noopener noreferrer"
                          {...props}
                        >
                          {children}
                        </a>
                      ),
                      p: ({ node, children, ...props }: any) => (
                        <p className="mb-2 last:mb-0" {...props}>
                          {children}
                        </p>
                      ),
                      ul: ({ node, children, ...props }: any) => (
                        <ul
                          className="list-disc list-inside space-y-1"
                          {...props}
                        >
                          {children}
                        </ul>
                      ),
                      ol: ({ node, children, ...props }: any) => (
                        <ol
                          className="list-decimal list-inside space-y-1"
                          {...props}
                        >
                          {children}
                        </ol>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

export const ChatMessage = memo(ChatMessageComponent);
