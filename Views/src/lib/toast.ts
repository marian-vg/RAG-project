import { writable } from 'svelte/store';

export type ToastType = 'success' | 'warning' | 'error';

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
  timeoutId: ReturnType<typeof setTimeout>;
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);
  let nextId = 0;

  return {
    subscribe,
    show(message: string, type: ToastType = 'success', duration = 5000) {
      const id = nextId++;
      const timeoutId = setTimeout(() => {
        this.remove(id);
      }, duration);

      update(toasts => [...toasts, { id, type, message, timeoutId }]);
      return id;
    },
    remove(id: number) {
      update(toasts => {
        const toast = toasts.find(t => t.id === id);
        if (toast) {
          clearTimeout(toast.timeoutId);
        }
        return toasts.filter(t => t.id !== id);
      });
    }
  };
}

export const toasts = createToastStore();