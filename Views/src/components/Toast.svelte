<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { X, CheckCircle, AlertTriangle, XCircle } from 'lucide-svelte';
  import { toasts, type ToastType } from '../lib/toast';

  function getIcon(type: ToastType) {
    switch (type) {
      case 'success': return CheckCircle;
      case 'warning': return AlertTriangle;
      case 'error': return XCircle;
    }
  }
</script>

<div class="fixed top-4 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 w-full max-w-md px-4">
  {#each $toasts as toast (toast.id)}
    <div
      class="flex items-center gap-3 p-4 rounded-xl shadow-lg border backdrop-blur-sm"
      class:bg-emerald-50={toast.type === 'success'}
      class:border-emerald-200={toast.type === 'success'}
      class:text-emerald-800={toast.type === 'success'}
      class:bg-amber-50={toast.type === 'warning'}
      class:border-amber-200={toast.type === 'warning'}
      class:text-amber-800={toast.type === 'warning'}
      class:bg-red-50={toast.type === 'error'}
      class:border-red-200={toast.type === 'error'}
      class:text-red-800={toast.type === 'error'}
      in:fly={{ y: -20, duration: 200 }}
      out:fade={{ duration: 150 }}
    >
      <svelte:component this={getIcon(toast.type)} size={20} />

      <p class="flex-1 text-sm font-medium">{toast.message}</p>

      <button
        onclick={() => toasts.remove(toast.id)}
        class="p-1 rounded-lg hover:bg-black/5 transition-colors"
        aria-label="Cerrar notificación"
      >
        <X size={16} />
      </button>
    </div>
  {/each}
</div>