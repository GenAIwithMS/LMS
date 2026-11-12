import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Trash2, Minimize2, MessageSquare } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { ChatPendingActions } from './ChatPendingActions';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatbotWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ isOpen, onClose }) => {
  // The conversation is saved on the server. It is loaded the first time the widget opens.
  const { messages, pendingActions, loading, sendMessage, answerAction, clearChat } = useChat(isOpen);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Adjustability states
  const [width, setWidth] = useState(() => {
    const saved = localStorage.getItem('chatbotWidth');
    return saved ? parseInt(saved, 10) : 400;
  });
  const [isResizing, setIsResizing] = useState(false);
  const resizeStartRef = useRef<{ x: number; width: number } | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, pendingActions]);

  useEffect(() => {
    localStorage.setItem('chatbotWidth', width.toString());
  }, [width]);

  // Handle resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing && resizeStartRef.current) {
        const deltaX = resizeStartRef.current.x - e.clientX;
        const newWidth = Math.max(320, Math.min(800, resizeStartRef.current.width + deltaX));
        setWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      resizeStartRef.current = null;
      document.body.style.cursor = 'default';
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'ew-resize';
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
      width: width,
    };
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    await sendMessage(userMessage);
  };

  return (
    <div 
      className={`fixed inset-y-0 right-0 bg-white z-[60] flex flex-col border-l border-gray-200 transition-transform duration-200 ease-out ${
        isOpen ? 'translate-x-0 shadow-[-12px_0_32px_-16px_rgba(28,27,24,0.3)]' : 'translate-x-full'
      }`}
      style={{ width: `${width}px` }}
    >
      {/* Resize Handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1.5 cursor-ew-resize hover:bg-primary-400/30 transition-colors z-10"
        onMouseDown={handleResizeStart}
      />

      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-white shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-600 rounded-md flex items-center justify-center text-white">
            <MessageSquare size={18} />
          </div>
          <div>
            <h3 className="font-serif text-lg font-semibold text-gray-900 leading-tight">Assistant</h3>
            <p className="text-xs text-gray-500">Answers from the school's records</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={clearChat} className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Clear Chat">
            <Trash2 size={18} />
          </button>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Minimize2 size={18} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50/50">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-3 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center ${
                message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200 text-primary-600 shadow-sm'
              }`}>
                {message.role === 'user' ? <User size={16} /> : <MessageSquare size={16} />}
              </div>
              <div className={`p-3.5 rounded-2xl text-sm shadow-sm ${
                message.role === 'user' 
                  ? 'bg-primary-600 text-white rounded-tr-none' 
                  : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
              }`}>
                <div className={`markdown-content ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        ))}
        <ChatPendingActions actions={pendingActions} disabled={loading} onAnswer={answerAction} />
        {loading && (
          <div className="flex justify-start">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-white border border-gray-200 text-primary-600 flex items-center justify-center shadow-sm">
                <MessageSquare size={16} />
              </div>
              <div className="bg-white border border-gray-100 p-4 rounded-2xl rounded-tl-none shadow-sm">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse"></div>
                  <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse [animation-delay:0.2s]"></div>
                  <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse [animation-delay:0.4s]"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-100 shrink-0">
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything..."
            className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all text-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:hover:bg-primary-600 transition-colors "
          >
            <Send size={16} />
          </button>
        </form>
        <p className="text-[10px] text-center text-gray-400 mt-3 font-medium">
          The assistant can make mistakes. Check anything important.
        </p>
      </div>
    </div>
  );
};

export default ChatbotWidget;
