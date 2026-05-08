<script lang="ts">
  import { Send, Bot, Loader2, FileText, Pill, Settings, Activity } from 'lucide-svelte';
  import Sidebar from './components/Sidebar.svelte';
  import ChatWindow from './components/ChatWindow.svelte';
  import Toast from './components/Toast.svelte';
  import { toasts } from './lib/toast';
  import { onMount } from 'svelte';

  interface Message {
    role: 'user' | 'assistant' | 'error';
    content: string;
  }

  let messages = $state<Message[]>([
    { role: 'assistant', content: 'Hola, soy **Farmy**, tu Auditor de Farmacia. ¿En qué puedo ayudarte hoy con las normativas de DIM, COFAER o PAMI?' }
  ]);
  let input = $state('');
  let isLoading = $state(false);
  let isSidebarOpen = $state(false);
  let provider = $state('ollama');
  let model = $state('qwen2.5:0.5b');
  let isSavingConfig = $state(false);
  let messagesEndRef = $state<HTMLDivElement | null>(null);
  let lastConfigChange = 0;
  const CONFIG_CHANGE_COOLDOWN = 500;
  let modelAliases = $state<Record<string, string>>({});

  let friendlyModelName = $derived(
    Object.keys(modelAliases).find(k => modelAliases[k] === model) || model
  );

  onMount(async () => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('http://localhost:8000/');
        if (response.ok) {
          const data = await response.json();

          if (data.current_model) {
            model = data.current_model;
          }
          if (data.current_provider) provider = data.current_provider;
        }
      } catch (err) {
        console.error("Error conectando con el backend:", err);
      }
    };

    const fetchAliases = async () => {
      try {
        const response = await fetch('http://localhost:8000/aliases');
        if (response.ok) {
          const data = await response.json();
          modelAliases = data.friendly_to_technical || {};
        }
      } catch (err) {
        console.error("Error fetching aliases:", err);
      }
    };

    await fetchConfig();
    await fetchAliases();
  });

  async function handleSend(overrideInput?: string) {
    const textToSend = overrideInput || input;
    if (!textToSend.trim() || isLoading) return;

    if (!overrideInput) input = '';

    messages = [...messages, { role: 'user', content: textToSend }];

    isLoading = true;

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

      if (data.fallback_triggered) {
        toasts.show(
          `Fallback: usando modelo ${data.provider_used === 'ollama' ? 'Qwen 2.5' : 'Gemini 2.5'}`,
          'warning'
        );
      }

      messages = [...messages, { role: 'assistant', content: data.answer }];

    } catch (error: any) {
      const msg = error.message === 'Failed to fetch' ? 'Servidor desconectado' : error.message;
      messages = [...messages, { role: 'error', content: `Error: ${msg}` }];
      toasts.show(msg, 'error');
    } finally {
      isLoading = false;
    }
  }

  async function handleConfigChange(newProvider: string, newModel: string) {
    const now = Date.now();

    if (newProvider === provider && newModel === model) {
      return;
    }

    if (now - lastConfigChange < CONFIG_CHANGE_COOLDOWN) {
      return;
    }
    lastConfigChange = now;

    const reallyChanged = newProvider !== provider || newModel !== model;
    provider = newProvider;
    model = newModel;
    isSavingConfig = true;

    try {
      const response = await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_provider: newProvider, llm_model: newModel }),
      });

      if (!response.ok) throw new Error("Error guardando config");

      if (reallyChanged) {
        toasts.show(`Configuración guardada: ${newProvider} (${friendlyModelName})`, 'success');
      }

    } catch (err: any) {
      console.error(err);
      toasts.show('Error al guardar configuración', 'error');
    } finally {
      setTimeout(() => isSavingConfig = false, 800);
    }
  }
</script>

<Toast />

<div class="flex h-screen bg-slate-100 overflow-hidden font-sans">
  <div class={`flex flex-col flex-1 transition-all duration-300 ${isSidebarOpen ? 'pr-80' : 'pr-0'}`}>
    <header class="flex items-center justify-between px-8 py-5 bg-white border-b border-slate-200/60 shadow-sm z-10">
      <div class="flex items-center gap-4">
        <div class="p-3 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-500 text-white shadow-lg shadow-teal-200">
          <Pill size={24} />
        </div>
        <div>
          <h1 class="text-2xl font-black text-slate-800 tracking-tight">Farmy <span class="text-teal-600 font-medium">Consulta</span></h1>
          <div class="flex items-center gap-2">
            <span class="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">RAG Auditor Activo</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <div class="hidden md:flex items-center gap-6 px-4 py-2 bg-slate-50 rounded-2xl border border-slate-100">
          <div class="flex flex-col">
            <span class="text-[8px] font-black text-slate-400 uppercase tracking-tighter">Modelo</span>
            <span class="text-xs font-bold text-slate-600">{friendlyModelName}</span>
          </div>
          <div class="w-px h-6 bg-slate-200"></div>
          <div class="flex flex-col">
            <span class="text-[8px] font-black text-slate-400 uppercase tracking-tighter">Latencia</span>
            <span class="text-xs font-bold text-teal-600 flex items-center gap-1"><Activity size={12}/> Optimizada</span>
          </div>
        </div>

        <button
          onclick={() => isSidebarOpen = !isSidebarOpen}
          class={`p-3 rounded-2xl transition-all shadow-sm ${
            isSidebarOpen ? 'bg-teal-600 text-white shadow-teal-200' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          <Settings size={22} />
        </button>
      </div>
    </header>

    <ChatWindow
      {messages}
      {isLoading}
      onFAQClick={handleSend}
      endRef={messagesEndRef}
    />

    <footer class="p-8 bg-white border-t border-slate-200/60 z-10">
      <div class="max-w-4xl mx-auto">
        <div class="relative group">
          <div class="absolute -inset-1 bg-gradient-to-r from-teal-500 to-emerald-500 rounded-3xl blur opacity-10 group-focus-within:opacity-25 transition duration-500"></div>
          <div class="relative flex items-center bg-slate-50 border border-slate-100 rounded-2xl p-2 transition-all group-focus-within:bg-white group-focus-within:border-teal-500/30 group-focus-within:shadow-xl group-focus-within:shadow-teal-100/50">
            <input
              type="text"
              bind:value={input}
              onkeydown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Escribe tu consulta sobre normativas aquí..."
              class="flex-1 pl-4 py-4 bg-transparent outline-none text-slate-700 placeholder:text-slate-400 font-medium"
            />
            <button
              onclick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              class="p-4 rounded-xl bg-teal-600 text-white hover:bg-teal-700 disabled:opacity-50 disabled:grayscale transition-all shadow-lg shadow-teal-200 active:scale-95"
            >
              {#if isLoading}
                <Loader2 class="animate-spin" size={24} />
              {:else}
                <Send size={24} />
              {/if}
            </button>
          </div>
        </div>
        <div class="mt-6 flex items-center justify-between">
          <div class="flex items-center gap-4 text-[10px] text-slate-400 font-black uppercase tracking-widest">
            <span class="flex items-center gap-1.5"><FileText size={14} class="text-teal-500"/> Normativas 2026</span>
            <span class="w-1 h-1 bg-slate-300 rounded-full"></span>
            <span class="flex items-center gap-1.5"><Bot size={14} class="text-emerald-500"/> IA Auditada</span>
          </div>
          <p class="text-[10px] text-slate-300 font-medium">Farmy Consulta v1.3 • Powered by LangChain</p>
        </div>
      </div>
    </footer>
  </div>

  <Sidebar
    bind:open={isSidebarOpen}
    {provider}
    {model}
    {friendlyModelName}
    onConfigChange={handleConfigChange}
    {isSavingConfig}
    {modelAliases}
  />
</div>
