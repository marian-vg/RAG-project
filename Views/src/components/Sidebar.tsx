import React from 'react';
import { Settings, X, Database, Cpu, CheckCircle2, AlertCircle } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  provider: string;
  model: string;
  onConfigChange: (provider: string, model: string) => void;
  isSaving: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  isOpen, 
  setIsOpen, 
  provider, 
  model, 
  onConfigChange,
  isSaving 
}) => {
  return (
    <>
      {/* Overlay para móviles */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Panel */}
      <aside className={`fixed top-0 right-0 h-full w-80 bg-white border-l border-slate-100 shadow-2xl z-50 transition-transform duration-300 transform ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-slate-50">
            <div className="flex items-center gap-2 text-teal-600">
              <Settings size={20} className="animate-spin-slow" />
              <h2 className="font-bold text-slate-800">Configuración</h2>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-slate-50 rounded-lg text-slate-400 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {/* LLM Provider Section */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                <Database size={14} />
                <span>Proveedor de IA</span>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {['ollama', 'gemini'].map((p) => (
                  <button
                    key={p}
                    onClick={() => onConfigChange(p, p === 'ollama' ? 'qwen2.5:0.5b' : 'gemini-1.5-flash')}
                    className={`flex items-center justify-between p-3 rounded-xl border-2 transition-all ${
                      provider === p 
                        ? 'border-teal-500 bg-teal-50 text-teal-700 shadow-sm shadow-teal-100' 
                        : 'border-slate-100 hover:border-slate-200 text-slate-500'
                    }`}
                  >
                    <span className="capitalize font-semibold">{p}</span>
                    {provider === p && <CheckCircle2 size={16} />}
                  </button>
                ))}
              </div>
            </section>

            {/* Model Section */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                <Cpu size={14} />
                <span>Modelo Seleccionado</span>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={model}
                  onChange={(e) => onConfigChange(provider, e.target.value)}
                  className="w-full p-3 bg-slate-50 border-2 border-slate-100 rounded-xl text-sm font-medium text-slate-700 focus:border-teal-500 focus:bg-white transition-all outline-none"
                  placeholder="Nombre del modelo..."
                />
              </div>
              <p className="text-[10px] text-slate-400 leading-relaxed italic">
                Asegúrate de que el modelo esté disponible en tu proveedor seleccionado.
              </p>
            </section>

            {/* System Status */}
            <section className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Estado del Sistema</h3>
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center">
                  <Database size={16} />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-700">Embeddings Locales</p>
                  <p className="text-[10px] text-emerald-600 font-medium">HuggingFace (MiniLM-L6)</p>
                </div>
              </div>
            </section>
          </div>

          {/* Footer - Save Status */}
          <div className="p-6 bg-slate-50/50 border-t border-slate-50">
            {isSaving ? (
              <div className="flex items-center gap-2 text-teal-600 text-sm font-bold animate-pulse">
                <div className="w-2 h-2 rounded-full bg-teal-500"></div>
                Guardando cambios...
              </div>
            ) : (
              <div className="flex items-center gap-2 text-slate-400 text-[10px] font-bold uppercase tracking-widest">
                <CheckCircle2 size={14} />
                Configuración Sincronizada
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
