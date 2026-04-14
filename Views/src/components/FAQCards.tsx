import React from 'react';
import { HelpCircle, FileText, AlertTriangle } from 'lucide-react';

interface FAQItem {
  question: string;
  label: string;
  icon: React.ReactNode;
}

interface FAQCardsProps {
  onFAQClick: (question: string) => void;
}

const faqs: FAQItem[] = [
  {
    question: "¿Cuáles son las normativas vigentes de PAMI?",
    label: "Normativas PAMI",
    icon: <FileText className="text-teal-500" size={24} />
  },
  {
    question: "¿Qué sucede con las recetas físicas de OSER desde 2026?",
    label: "Decreto OSER",
    icon: <AlertTriangle className="text-emerald-500" size={24} />
  },
  {
    question: "¿Qué requisitos tienen las recetas veterinarias en DIM?",
    label: "Recetas DIM",
    icon: <HelpCircle className="text-teal-600" size={24} />
  }
];

const FAQCards: React.FC<FAQCardsProps> = ({ onFAQClick }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-4xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {faqs.map((faq, index) => (
        <button
          key={index}
          onClick={() => onFAQClick(faq.question)}
          className="group flex flex-col items-start p-6 bg-white border border-slate-100 rounded-3xl shadow-sm hover:shadow-xl hover:border-teal-500/30 transition-all duration-300 text-left active:scale-95"
        >
          <div className="p-3 rounded-2xl bg-slate-50 group-hover:bg-teal-50 transition-colors mb-4">
            {faq.icon}
          </div>
          <h3 className="font-bold text-slate-800 mb-2 group-hover:text-teal-700 transition-colors">
            {faq.label}
          </h3>
          <p className="text-xs text-slate-400 font-medium leading-relaxed line-clamp-2">
            {faq.question}
          </p>
        </button>
      ))}
    </div>
  );
};

export default FAQCards;
