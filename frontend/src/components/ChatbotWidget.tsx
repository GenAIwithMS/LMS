import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, X, ChevronRight, ChevronLeft } from 'lucide-react';
import { chatWithBot } from '../services/api';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatbotWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  onWidthChange?: (width: number) => void;
  onCollapseChange?: (collapsed: boolean) => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ isOpen, onClose, onWidthChange, onCollapseChange }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your LMS assistant. How can I help you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [chatbotCollapsed, setChatbotCollapsed] = useState(false);
  const [chatbotWidth, setChatbotWidth] = useState(400);
  const [isResizing, setIsResizing] = useState(false);
  const resizeStartRef = useRef<{ x: number; width: number } | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Notify parent of width changes
  useEffect(() => {
    if (onWidthChange) {
      // Notify with actual displayed width (64px when collapsed)
      onWidthChange(chatbotCollapsed ? 64 : chatbotWidth);
    }
  }, [chatbotCollapsed, chatbotWidth, onWidthChange]);

  // Handle chatbot sidebar resize
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing && resizeStartRef.current) {
        const deltaX = resizeStartRef.current.x - e.clientX; // Inverted because sidebar is on right
        const newWidth = Math.max(300, Math.min(600, resizeStartRef.current.width + deltaX));
        setChatbotWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      resizeStartRef.current = null;
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    resizeStartRef.current = {
      x: e.clientX,
      width: chatbotWidth,
    };
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await chatWithBot(userMessage);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.message || 'I apologize, but I couldn\'t process that request.' },
      ]);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to get response');
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // When collapsed, show a small width to keep the toggle button accessible
  const displayWidth = chatbotCollapsed ? 64 : chatbotWidth;

  if (!isOpen) return null;

  return (
    <aside
      className={`fixed top-0 right-0 z-50 h-full bg-white shadow-lg transition-all duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}
      style={{ width: `${displayWidth}px` }}
    >
      <div className="flex flex-col h-full relative">
        {/* Resize Handle */}
        {!chatbotCollapsed && (
          <div
            className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-primary-200 bg-transparent transition-colors z-10"
            onMouseDown={handleResizeStart}
          />
        )}

        {/* Collapse Toggle Button */}
        <button
          onClick={() => {
            const newCollapsed = !chatbotCollapsed;
            setChatbotCollapsed(newCollapsed);
            if (onCollapseChange) {
              onCollapseChange(newCollapsed);
            }
          }}
          className="absolute -left-4 top-4 bg-white rounded-full p-1 shadow-md hover:bg-gray-100 transition-colors z-20 border border-gray-200"
          title={chatbotCollapsed ? 'Expand chatbot' : 'Collapse chatbot'}
        >
          {chatbotCollapsed ? (
            <ChevronLeft size={20} className="text-gray-600" />
          ) : (
            <ChevronRight size={20} className="text-gray-600" />
          )}
        </button>

        {/* Collapsed state - show minimal UI */}
        {chatbotCollapsed && (
          <div className="h-full flex items-center justify-center">
            <Bot size={20} className="text-gray-400" />
          </div>
        )}

        {/* Header */}
        {!chatbotCollapsed && (
          <>
            <div className="bg-primary-600 text-white px-4 py-3 flex items-center justify-between border-b">
              <div className="flex items-center space-x-2">
                <Bot size={20} />
                <span className="font-semibold">LMS Assistant</span>
              </div>
              <button
                onClick={onClose}
                className="p-1 hover:bg-primary-700 rounded transition-colors"
                title="Close"
              >
                <X size={18} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-start space-x-3 ${
                    message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}
                >
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                  </div>
                  <div
                    className={`flex-1 rounded-lg p-3 max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-900 border border-gray-200'
                    }`}
                  >
                    <div className={`markdown-content text-sm ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center">
                    <Bot size={18} />
                  </div>
                  <div className="flex-1 rounded-lg p-3 bg-white border border-gray-200">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="border-t p-4 bg-white">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 input text-sm"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="btn btn-primary px-4"
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </aside>
  );
};

export default ChatbotWidget;
