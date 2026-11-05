import { useState, useEffect } from 'react';
import { chatWithBot, getChatHistory, clearChatHistory, answerChatAction } from '../services/api';
import toast from 'react-hot-toast';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// A delete or edit the assistant asked for, waiting for the user to click Confirm or Cancel
export interface PendingAction {
  id: number;
  description: string;
}

const GREETING: ChatMessage = {
  role: 'assistant',
  content: "Hello! I'm your LMS AI assistant. How can I help you today?",
};

// Shared by the chat widget and the chat page, so both behave the same.
// The conversation is saved on the server; this hook loads it and keeps it on screen.
// "enabled" lets the widget wait until it is opened before loading the history.
export const useChat = (enabled: boolean = true) => {
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [pendingActions, setPendingActions] = useState<PendingAction[]>([]);
  const [loading, setLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  useEffect(() => {
    if (enabled && !historyLoaded) {
      loadHistory();
    }
  }, [enabled, historyLoaded]);

  const loadHistory = async () => {
    try {
      const data = await getChatHistory();
      if (data.messages && data.messages.length > 0) {
        setMessages(data.messages);
      }
      setPendingActions(data.pending_actions || []);
    } catch (error: any) {
      toast.error('Could not load your chat history');
    } finally {
      setHistoryLoaded(true);
    }
  };

  const sendMessage = async (text: string) => {
    const userMessage = text.trim();
    if (!userMessage || loading) {
      return;
    }

    setMessages((previous) => [...previous, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await chatWithBot(userMessage);
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: response.message || "I apologize, but I couldn't process that request." },
      ]);
      setPendingActions(response.pending_actions || []);
    } catch (error: any) {
      // Shown on screen only. It is not saved, so it never goes back to the assistant.
      // When the server says why (for example, the assistant isn't set up), show that reason
      const serverMessage: string | undefined = error.response?.data?.message;
      toast.error(serverMessage || 'Failed to get response');
      let bubbleText = 'Sorry, I encountered an error. Please try again.';
      if (serverMessage) {
        bubbleText = serverMessage;
      }
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: bubbleText },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // approve = true: the user clicked Confirm. false: Cancel.
  const answerAction = async (actionId: number, approve: boolean) => {
    setLoading(true);
    try {
      const response = await answerChatAction(actionId, approve);
      setMessages((previous) => [...previous, { role: 'assistant', content: response.message }]);
      setPendingActions(response.pending_actions || []);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Could not complete the action');
      // Reload, in case the action was already handled in another tab
      setHistoryLoaded(false);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await clearChatHistory();
      setMessages([GREETING]);
      setPendingActions([]);
      toast.success('Chat history cleared');
    } catch (error: any) {
      toast.error('Could not clear the chat history');
    }
  };

  return { messages, pendingActions, loading, sendMessage, answerAction, clearChat };
};
