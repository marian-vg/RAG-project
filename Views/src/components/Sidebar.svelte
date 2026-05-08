<script lang="ts">
  import { Settings, X, Database, Cpu, CheckCircle2 } from 'lucide-svelte';
  import { slide, fade } from 'svelte/transition';

  interface Props {
    open: boolean;
    provider: string;
    model: string;
    friendlyModelName: string;
    onConfigChange: (provider: string, model: string) => void;
    isSavingConfig: boolean;
    modelAliases?: Record<string, string>;
  }

  let {
    open = $bindable(false),
    provider,
    model,
    friendlyModelName,
    onConfigChange,
    isSavingConfig,
    modelAliases = {}
  }: Props = $props();

  function handleProviderSelect(p: string) {
    const defaultModel = p === 'ollama' ? 'qwen2.5:0.5b' : 'models/gemini-2.5-flash';
    onConfigChange(p, defaultModel);
  }

  function handleModelChange(e: Event) {
    const input = (e.currentTarget as HTMLInputElement).value;
    const technical = modelAliases[input] || input;
    onConfigChange(provider, technical);
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
    transition:fade={{ duration: 200 }}
    onclick={() => open = false}
    role="button"
    tabindex="-1"
    aria-label="Cerrar sidebar"
  ></div>
{/if}

<aside
  class={`fixed top-0 right-0 h-full w-80 bg-white border-l border-slate-100 shadow-2xl z-50 transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}
  transition:slide={{ duration: 300, axis: 'x' }}
>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between px-6 py-5 border-b border-slate-50">
      <div class="flex items-center gap-2 text-teal-600">
        <Settings size={20} />
        <h2 class="font-bold text-slate-800">Configuración</h2>
      </div>
      <button
        onclick={() => open = false}
        class="p-2 hover:bg-slate-50 rounded-lg text-slate-400 transition-colors"
        aria-label="Cerrar configuración"
      >
        <X size={20} />
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-6 space-y-8">
      <section class="space-y-4">
        <div class="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
          <Database size={14} />
          <span>Proveedor de IA</span>
        </div>
        <div class="grid grid-cols-1 gap-2">
          {#each ['ollama', 'gemini'] as p}
            <button
              onclick={() => handleProviderSelect(p)}
              class={`flex items-center justify-between p-3 rounded-xl border-2 transition-all ${
                provider === p
                  ? 'border-teal-500 bg-teal-50 text-teal-700 shadow-sm shadow-teal-100'
                  : 'border-slate-100 hover:border-slate-200 text-slate-500'
              }`}
            >
              <span class="capitalize font-semibold">{p}</span>
              {#if provider === p}
                <CheckCircle2 size={16} />
              {/if}
            </button>
          {/each}
        </div>
      </section>

      <section class="space-y-4">
        <div class="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
          <Cpu size={14} />
          <span>Modelo Seleccionado</span>
        </div>
        <div class="relative">
          <input
            type="text"
            value={friendlyModelName}
            onchange={handleModelChange}
            class="w-full p-3 bg-slate-50 border-2 border-slate-100 rounded-xl text-sm font-medium text-slate-700 focus:border-teal-500 focus:bg-white transition-all outline-none"
            placeholder="Nombre del modelo..."
          />
          <p class="text-[10px] text-teal-600 mt-1 font-medium">
            Técnico: {model}
          </p>
        </div>
        <p class="text-[10px] text-slate-400 leading-relaxed italic">
          Asegúrate de que el modelo esté disponible en tu proveedor seleccionado.
        </p>
      </section>

      <section class="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Estado del Sistema</h3>
        <div class="flex items-center gap-3">
          <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <Database size={16} />
          </div>
          <div>
            <p class="text-xs font-bold text-slate-700">Embeddings Locales</p>
            <p class="text-[10px] text-emerald-600 font-medium">HuggingFace (MiniLM-L6)</p>
          </div>
        </div>
      </section>
    </div>

    <div class="p-6 bg-slate-50/50 border-t border-slate-50">
      {#if isSavingConfig}
        <div class="flex items-center gap-2 text-teal-600 text-sm font-bold animate-pulse">
          <div class="w-2 h-2 rounded-full bg-teal-500"></div>
          Guardando cambios...
        </div>
      {:else}
        <div class="flex items-center gap-2 text-slate-400 text-[10px] font-bold uppercase tracking-widest">
          <CheckCircle2 size={14} />
          Configuración Sincronizada
        </div>
      {/if}
    </div>
  </div>
</aside>
