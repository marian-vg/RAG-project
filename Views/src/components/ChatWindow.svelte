<script lang="ts">
  import { Bot, User, AlertCircle } from 'lucide-svelte';
  import { marked } from 'marked';
  import FAQCards from './FAQCards.svelte';

  interface Message {
    role: 'user' | 'assistant' | 'error';
    content: string;
  }

  interface Props {
    messages: Message[];
    isLoading: boolean;
    onFAQClick: (question: string) => void;
    endRef: HTMLDivElement | null;
  }

  let { messages, isLoading, onFAQClick, endRef = $bindable(null) }: Props = $props();

  function renderMarkdown(content: string): string {
    return marked.parse(content, { async: false }) as string;
  }

  function scrollToBottom() {
    if (endRef) {
      endRef.scrollIntoView({ behavior: 'smooth' });
    }
  }

  $effect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  });
</script>

<main class="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
  {#each messages as message, index (index)}
    <div class={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div class={`flex gap-4 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
        <div class={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-sm transition-transform hover:scale-105 ${
          message.role === 'user' ? 'bg-teal-100 text-teal-600' :
          message.role === 'error' ? 'bg-red-100 text-red-600' :
          'bg-white border border-slate-200 text-teal-600'
        }`}>
          {#if message.role === 'user'}
            <User size={20} />
          {:else if message.role === 'error'}
            <AlertCircle size={20} />
          {:else}
            <Bot size={20} />
          {/if}
        </div>
        <div class={`p-4 rounded-2xl shadow-sm transition-all ${
          message.role === 'user'
            ? 'bg-teal-600 text-white rounded-tr-none shadow-teal-100'
            : message.role === 'error'
            ? 'bg-red-50 border border-red-100 text-red-700 rounded-tl-none'
            : 'bg-white border border-slate-100 text-slate-700 rounded-tl-none hover:shadow-md'
        }`}>
          <div class={`prose prose-sm max-w-none ${message.role === 'user' ? 'prose-invert' : 'prose-slate'}`}>
            {@html renderMarkdown(message.content)}
          </div>
        </div>
      </div>
    </div>
  {/each}

  {#if isLoading}
    <div class="flex justify-start">
      <div class="flex gap-4 items-center">
        <div class="flex-shrink-0 w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center shadow-sm animate-pulse">
          <Bot size={20} class="text-teal-400" />
        </div>
        <div class="flex gap-1.5 p-4 bg-white border border-slate-100 rounded-2xl rounded-tl-none shadow-sm">
          <div class="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style="animation-delay: -0.3s"></div>
          <div class="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style="animation-delay: -0.15s"></div>
          <div class="w-2 h-2 bg-teal-400 rounded-full animate-bounce"></div>
        </div>
      </div>
    </div>
  {/if}

  {#if messages.length <= 1 && !isLoading}
    <FAQCards onFAQClick={onFAQClick} />
  {/if}
  <div bind:this={endRef}></div>
</main>