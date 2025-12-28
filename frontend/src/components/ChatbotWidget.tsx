import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, X, Minimize2, Maximize2 } from 'lucide-react';
import { chatWithBot } from '../services/api';
import toast from 'react-hot-toast';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatbotWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your LMS assistant. How can I help you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<HTMLDivElement>(null);
  // Initialize position and size based on screen size
  const [position, setPosition] = useState({ 
    x: Math.max(0, window.innerWidth - 420), 
    y: Math.max(0, (window.innerHeight - 600) / 2) 
  });
  const [size, setSize] = useState({ 
    width: Math.min(400, window.innerWidth - 40), 
    height: Math.min(600, window.innerHeight - 100) 
  });
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isOpen) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const newX = e.clientX - dragStart.x;
        const newY = e.clientY - dragStart.y;
        
        // Constrain to viewport
        const maxX = window.innerWidth - size.width;
        const maxY = window.innerHeight - (isMinimized ? 60 : size.height);
        
        setPosition({
          x: Math.max(0, Math.min(newX, maxX)),
          y: Math.max(0, Math.min(newY, maxY)),
        });
      } else if (isResizing) {
        const deltaX = e.clientX - resizeStart.x;
        const deltaY = e.clientY - resizeStart.y;
        
        // Minimum size: 400x400, Maximum: full screen (but keep some margin)
        const minWidth = 400;
        const minHeight = 400;
        const maxWidth = window.innerWidth - position.x - 20;
        const maxHeight = window.innerHeight - position.y - 20;
        
        // Allow resizing from minWidth to maxWidth (can be half screen or more)
        const newWidth = Math.max(minWidth, Math.min(resizeStart.width + deltaX, maxWidth));
        const newHeight = Math.max(minHeight, Math.min(resizeStart.height + deltaY, maxHeight));
        
        setSize({
          width: newWidth,
          height: newHeight,
        });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      setIsResizing(false);
    };

    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, isResizing, dragStart, resizeStart, size, position, isMinimized, isOpen]);

  const handleDragStart = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.resize-handle')) return;
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    });
  };

  const handleResizeStart = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsResizing(true);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height,
    });
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

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-20 z-40 modal-backdrop"
        onClick={onClose}
      />

      {/* Widget */}
      <div
        ref={widgetRef}
        className={`fixed bg-white rounded-lg shadow-2xl z-50 flex flex-col modal-content ${isMinimized ? 'overflow-hidden' : 'overflow-hidden'}`}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          width: `${size.width}px`,
          height: isMinimized ? '60px' : `${size.height}px`,
        }}
      >
        {/* Header - Draggable */}
        <div
          className="bg-primary-600 text-white px-4 py-3 flex items-center justify-between cursor-move select-none"
          onMouseDown={handleDragStart}
        >
          <div className="flex items-center space-x-2">
            <Bot size={20} />
            <span className="font-semibold">LMS Assistant</span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsMinimized(!isMinimized);
              }}
              className="p-1 hover:bg-primary-700 rounded transition-colors"
              title={isMinimized ? 'Maximize' : 'Minimize'}
            >
              {isMinimized ? <Maximize2 size={18} /> : <Minimize2 size={18} />}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="p-1 hover:bg-primary-700 rounded transition-colors"
              title="Close"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content */}
        {!isMinimized && (
          <div className="flex-1 flex flex-col overflow-hidden">
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
                    <p className="whitespace-pre-wrap text-sm">{message.content}</p>
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
          </div>
        )}

        {/* Resize Handle */}
        {!isMinimized && (
          <div
            className="resize-handle absolute bottom-0 right-0 w-6 h-6 cursor-nwse-resize bg-gray-200 hover:bg-primary-200 transition-colors"
            onMouseDown={handleResizeStart}
            style={{
              backgroundImage: 'linear-gradient(-45deg, transparent 30%, #cbd5e1 30%, #cbd5e1 35%, transparent 35%, transparent 65%, #cbd5e1 65%, #cbd5e1 70%, transparent 70%)',
              backgroundSize: '12px 12px',
            }}
          />
        )}
      </div>
    </>
  );
};

export default ChatbotWidget;

