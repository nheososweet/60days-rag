/**
 * Chat Store - Zustand state management
 * 
 * Manages:
 * - Messages history
 * - Chat settings
 * - UI state (loading, errors)
 * - Streaming state
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ChatMessage, ChatSettings } from '@/lib/api/qwen';

interface ChatState {
  // Messages
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  updateLastMessage: (updates: Partial<ChatMessage>) => void;
  clearMessages: () => void;

  // Settings
  settings: ChatSettings;
  updateSettings: (updates: Partial<ChatSettings>) => void;

  // UI State
  isStreaming: boolean;
  setStreaming: (streaming: boolean) => void;
  
  error: string | null;
  setError: (error: string | null) => void;

  // Current streaming message
  currentThinking: string;
  currentContent: string;
  setCurrentThinking: (thinking: string) => void;
  setCurrentContent: (content: string) => void;
  appendCurrentContent: (chunk: string) => void;
  resetCurrent: () => void;
}

const defaultSettings: ChatSettings = {
  temperature: 0.7,
  maxTokens: 32768,
  enableThinking: true,
  systemPrompt: 'You are a helpful AI assistant with expertise in many topics. Show your reasoning process when enabled.',
};

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      messages: [],
      settings: defaultSettings,
      isStreaming: false,
      error: null,
      currentThinking: '',
      currentContent: '',

      // Message actions
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      updateLastMessage: (updates) =>
        set((state) => {
          const messages = [...state.messages];
          const lastIndex = messages.length - 1;
          
          if (lastIndex >= 0) {
            messages[lastIndex] = {
              ...messages[lastIndex],
              ...updates,
            };
          }
          
          return { messages };
        }),

      clearMessages: () =>
        set({
          messages: [],
          currentThinking: '',
          currentContent: '',
          error: null,
        }),

      // Settings actions
      updateSettings: (updates) =>
        set((state) => ({
          settings: {
            ...state.settings,
            ...updates,
          },
        })),

      // UI state actions
      setStreaming: (streaming) => set({ isStreaming: streaming }),
      
      setError: (error) => set({ error }),

      // Current streaming state
      setCurrentThinking: (thinking) => set({ currentThinking: thinking }),
      
      setCurrentContent: (content) => set({ currentContent: content }),
      
      appendCurrentContent: (chunk) =>
        set((state) => ({
          currentContent: state.currentContent + chunk,
        })),

      resetCurrent: () =>
        set({
          currentThinking: '',
          currentContent: '',
        }),
    }),
    {
      name: 'chat-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist settings and messages (not UI state)
        messages: state.messages,
        settings: state.settings,
      }),
    }
  )
);
