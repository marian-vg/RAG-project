import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2, FileText, Pill, Settings, Activity } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

interface Message {
  role: 'user' | 'assistant' | 'error';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hola, soy **Farmy**, tu Auditor de Farmacia. ¿En qué puedo ayudarte hoy con las normativas de DIM, COFAER o PAMI?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  // Backend State
  const [provider, setProvider] = useState('ollama');
  const [model, setModel] = useState('qwen2.5:0.5b');
  const [isSavingConfig, setIsSavingConfig] = useState(false);
  const [isOnline, setIsOnline] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Cargar configuración inicial
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('http://localhost:8000/');
        if (response.ok) {
          const data = await response.json();
          setIsOnline(data.engine_loaded);
          if (data.current_model) setModel(data.current_model);
          // Nota: El backend / no devuelve el provider actualmente, lo asumimos por ahora
        }
      } catch (err) {
        console.error("Error conectando con el backend:", err);
      }
    };
    fetchConfig();
  }, []);

  const handleSend = async (overrideInput?: string) => {
    const textToSend = overrideInput || input;
    if (!textToSend.trim() || isLoading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: textToSend }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: textToSend }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Error en el servidor' }));
        throw new Error(errorData.detail || 'Error en la respuesta');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (error: any) {
      const msg = error.message === 'Failed to fetch' ? 'Servidor desconectado' : error.message;
      setMessages(prev => [...prev, { role: 'error', content: `Error: ${msg}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfigChange = async (newProvider: string, newModel: string) => {
    setProvider(newProvider);
    setModel(newModel);
    setIsSavingConfig(true);

    try {
      const response = await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_provider: newProvider, llm_model: newModel }),
      });

      if (!response.ok) throw new Error("Error guardando config");
      
      const data = await response.json();
      console.log("Config actualizada:", data);
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsSavingConfig(false), 800);
    }
  };

  return (
    <div className="flex h-screen bg-slate-100 overflow-hidden font-sans">
      {/* Contenedor Principal */}
      <div className={`flex flex-col flex-1 transition-all duration-300 ${isSidebarOpen ? 'pr-80' : 'pr-0'}`}>
        
        {/* Header Moderno */}
        <header className="flex items-center justify-between px-8 py-5 bg-white border-b border-slate-200/60 shadow-sm z-10">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-500 text-white shadow-lg shadow-teal-200">
              <Pill size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-800 tracking-tight">Farmy <span className="text-teal-600 font-medium">Consulta</span></h1>
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">RAG Auditor Activo</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-6 px-4 py-2 bg-slate-50 rounded-2xl border border-slate-100">
              <div className="flex flex-col">
                <span className="text-[8px] font-black text-slate-400 uppercase tracking-tighter">Modelo</span>
                <span className="text-xs font-bold text-slate-600">{model}</span>
              </div>
              <div className="w-px h-6 bg-slate-200"></div>
              <div className="flex flex-col">
                <span className="text-[8px] font-black text-slate-400 uppercase tracking-tighter">Latencia</span>
                <span className="text-xs font-bold text-teal-600 flex items-center gap-1"><Activity size={12}/> Optimizada</span>
              </div>
            </div>
            
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className={`p-3 rounded-2xl transition-all shadow-sm ${
                isSidebarOpen ? 'bg-teal-600 text-white shadow-teal-200' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Settings size={22} />
            </button>
          </div>
        </header>

        {/* Chat Area Component */}
        <ChatWindow 
          messages={messages} 
          isLoading={isLoading} 
          messagesEndRef={messagesEndRef} 
          onFAQClick={handleSend}
        />

        {/* Input Area Moderna */}
        <footer className="p-8 bg-white border-t border-slate-200/60 z-10">
          <div className="max-w-4xl mx-auto">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-teal-500 to-emerald-500 rounded-3xl blur opacity-10 group-focus-within:opacity-25 transition duration-500"></div>
              <div className="relative flex items-center bg-slate-50 border border-slate-100 rounded-2xl p-2 transition-all group-focus-within:bg-white group-focus-within:border-teal-500/30 group-focus-within:shadow-xl group-focus-within:shadow-teal-100/50">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Escribe tu consulta sobre normativas aquí..."
                  className="flex-1 pl-4 py-4 bg-transparent outline-none text-slate-700 placeholder:text-slate-400 font-medium"
                />
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className="p-4 rounded-xl bg-teal-600 text-white hover:bg-teal-700 disabled:opacity-50 disabled:grayscale transition-all shadow-lg shadow-teal-200 active:scale-95"
                >
                  {isLoading ? <Loader2 className="animate-spin" size={24} /> : <Send size={24} />}
                </button>
              </div>
            </div>
            <div className="mt-6 flex items-center justify-between">
               <div className="flex items-center gap-4 text-[10px] text-slate-400 font-black uppercase tracking-widest">
                <span className="flex items-center gap-1.5"><FileText size={14} className="text-teal-500"/> Normativas 2026</span>
                <span className="w-1 h-1 bg-slate-300 rounded-full"></span>
                <span className="flex items-center gap-1.5"><Bot size={14} className="text-emerald-500"/> IA Auditada</span>
              </div>
              <p className="text-[10px] text-slate-300 font-medium">Farmy Consulta v1.3 • Powered by LangChain</p>
            </div>
          </div>
        </footer>
      </div>

      {/* Config Sidebar Component */}
      <Sidebar 
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        provider={provider}
        model={model}
        onConfigChange={handleConfigChange}
        isSaving={isSavingConfig}
      />
    </div>
  );
}

export default App;
