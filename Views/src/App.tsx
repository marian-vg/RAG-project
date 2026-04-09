import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, FileText, Pill, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant' | 'error';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hola, soy tu Auditor de Farmacia FarmaRAG. ¿En qué puedo ayudarte hoy con las normativas de DIM, COFAER o PAMI?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Error desconocido en el servidor' }));
        throw new Error(errorData.detail || 'Error en la respuesta del servidor');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (error: any) {
      console.error('Error:', error);
      const errorMessage = error.message === 'Failed to fetch' 
        ? 'No se pudo conectar con el servidor. Asegúrese de que server.py esté ejecutándose en el puerto 8000.'
        : `Error: ${error.message}`;
      
      setMessages(prev => [...prev, { role: 'error', content: errorMessage }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white shadow-2xl">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-sky-500 text-white">
            <Pill size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800">FarmaRAG</h1>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Auditor de Farmacia Inteligente</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs font-semibold text-slate-500">Sistema Online</span>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-3 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                message.role === 'user' ? 'bg-sky-100 text-sky-600' : 
                message.role === 'error' ? 'bg-red-100 text-red-600' :
                'bg-white border border-slate-200 text-slate-600 shadow-sm'
              }`}>
                {message.role === 'user' ? <User size={18} /> : 
                 message.role === 'error' ? <AlertCircle size={18} /> :
                 <Bot size={18} />}
              </div>
              <div className={`p-4 rounded-2xl shadow-sm ${
                message.role === 'user' ? 'bg-sky-600 text-white rounded-tr-none' : 
                message.role === 'error' ? 'bg-red-50 border border-red-100 text-red-700 rounded-tl-none' :
                'bg-white border border-slate-100 text-slate-700 rounded-tl-none'
              }`}>
                <div className="prose prose-sm max-w-none prose-slate">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-3 items-center text-slate-400">
              <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center">
                <Bot size={18} />
              </div>
              <div className="flex gap-1 animate-pulse">
                <div className="w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="p-6 bg-white border-t border-slate-100">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Consulte normativas de DIM, COFAER o PAMI..."
            className="w-full pl-4 pr-14 py-4 bg-slate-100 border-none rounded-2xl focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all outline-none text-slate-700 placeholder:text-slate-400"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2.5 rounded-xl bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-50 disabled:bg-slate-300 transition-all shadow-lg shadow-sky-200"
          >
            {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
          </button>
        </div>
        <div className="mt-4 flex items-center gap-4 text-[10px] text-slate-400 font-bold uppercase tracking-widest justify-center">
          <span className="flex items-center gap-1"><FileText size={12}/> Normativas Actualizadas</span>
          <span className="flex items-center gap-1"><Bot size={12}/> Basado en RAG</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
