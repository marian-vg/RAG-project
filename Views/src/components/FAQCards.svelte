<script lang="ts">
  import { HelpCircle, FileText, AlertTriangle } from 'lucide-svelte';

  interface FAQItem {
    question: string;
    label: string;
    icon: 'file' | 'alert' | 'help';
  }

  interface Props {
    onFAQClick: (question: string) => void;
  }

  let { onFAQClick }: Props = $props();

  const faqs: FAQItem[] = [
    {
      question: "¿Cuáles son las normativas vigentes de PAMI?",
      label: "Normativas PAMI",
      icon: 'file'
    },
    {
      question: "¿Qué sucede con las recetas físicas de OSER desde 2026?",
      label: "Decreto OSER",
      icon: 'alert'
    },
    {
      question: "¿Qué requisitos tienen las recetas veterinarias en DIM?",
      label: "Recetas DIM",
      icon: 'help'
    }
  ];

  function getIconComponent(icon: 'file' | 'alert' | 'help') {
    switch (icon) {
      case 'file': return FileText;
      case 'alert': return AlertTriangle;
      case 'help': return HelpCircle;
    }
  }
</script>

<div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-4xl mx-auto mt-8">
  {#each faqs as faq, index (index)}
    <button
      onclick={() => onFAQClick(faq.question)}
      class="group flex flex-col items-start p-6 bg-white border border-slate-100 rounded-3xl shadow-sm hover:shadow-xl hover:border-teal-500/30 transition-all duration-300 text-left active:scale-95"
    >
      <div class="p-3 rounded-2xl bg-slate-50 group-hover:bg-teal-50 transition-colors mb-4">
        {#if faq.icon === 'file'}
          <FileText class="text-teal-500" size={24} />
        {:else if faq.icon === 'alert'}
          <AlertTriangle class="text-emerald-500" size={24} />
        {:else}
          <HelpCircle class="text-teal-600" size={24} />
        {/if}
      </div>
      <h3 class="font-bold text-slate-800 mb-2 group-hover:text-teal-700 transition-colors">
        {faq.label}
      </h3>
      <p class="text-xs text-slate-400 font-medium leading-relaxed line-clamp-2">
        {faq.question}
      </p>
    </button>
  {/each}
</div>