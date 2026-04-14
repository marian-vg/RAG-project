import React from 'react';
import { Bot, User, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import FAQCards from './FAQCards';

interface Message {
  role: 'user' | 'assistant' | 'error';
  content: string;
}

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  onFAQClick: (question: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading, messagesEndRef, onFAQClick }) => {
  return (
    <main className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
      {messages.map((message, index) => (
        <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`flex gap-4 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
            <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-sm transition-transform hover:scale-105 ${
              message.role === 'user' ? 'bg-teal-100 text-teal-600' : 
              message.role === 'error' ? 'bg-red-100 text-red-600' :
              'bg-white border border-slate-200 text-teal-600'
            }`}>
              {message.role === 'user' ? <User size={20} /> : 
               message.role === 'error' ? <AlertCircle size={20} /> :
               <Bot size={20} />}
            </div>
            <div className={`p-4 rounded-2xl shadow-sm transition-all ${
              message.role === 'user' 
                ? 'bg-teal-600 text-white rounded-tr-none shadow-teal-100' 
                : message.role === 'error' 
                ? 'bg-red-50 border border-red-100 text-red-700 rounded-tl-none' 
                : 'bg-white border border-slate-100 text-slate-700 rounded-tl-none hover:shadow-md'
            }`}>
              <div className={`prose prose-sm max-w-none ${message.role === 'user' ? 'prose-invert' : 'prose-slate'}`}>
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="flex justify-start">
          <div className="flex gap-4 items-center">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center shadow-sm animate-pulse">
              <Bot size={20} className="text-teal-400" />
            </div>
            <div className="flex gap-1.5 p-4 bg-white border border-slate-100 rounded-2xl rounded-tl-none shadow-sm">
              <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"></div>
            </div>
          </div>
        </div>
      )}

      {messages.length <= 1 && !isLoading && (
        <FAQCards onFAQClick={onFAQClick} />
      )}
      <div ref={messagesEndRef} />
    </main>
  );
};

export default ChatWindow;
