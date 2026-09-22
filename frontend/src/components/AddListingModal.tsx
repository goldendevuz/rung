import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchCategories, createListing } from '../api/client';

interface AddListingModalProps {
  onClose: () => void;
}

export default function AddListingModal({ onClose }: AddListingModalProps) {
  const [kind] = useState('channel'); // Hozircha faqat kanal
  const [handle, setHandle] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const { data: categories, isLoading: isCategoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsCategoryOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const mutation = useMutation({
    mutationFn: createListing,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-listings'] });
      onClose();
    },
    onError: (err: Error) => {
      alert(err.message || "Xatolik yuz berdi");
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!handle.trim() || !name.trim() || !category) {
      alert("Iltimos, barcha kerakli maydonlarni to'ldiring.");
      return;
    }
    mutation.mutate({
      kind,
      handle: handle.trim(),
      name: name.trim(),
      description: description.trim(),
      category_slug: category
    });
  };

  const selectedCategoryObj = categories?.find((c: any) => c.slug === category);

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in"
      style={{ animation: 'fadeIn 0.15s ease-out' }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div 
        className="w-full max-w-lg bg-[#12151A] border border-white/10 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden"
        style={{
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.08)'
        }}
      >
        {/* Top Accent Line */}
        <div 
          className="absolute top-0 left-0 right-0 h-1"
          style={{ background: 'linear-gradient(90deg, #B8F03C, #4ADE80, #3B82F6)' }}
        />

        {/* Close Button */}
        <button 
          onClick={onClose}
          type="button"
          aria-label="Yopish"
          className="absolute top-5 right-5 w-8 h-8 rounded-full flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors"
        >
          ✕
        </button>
        
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">📢</span>
            <h2 className="text-xl font-bold text-white tracking-tight">Yangi kanal qo'shish</h2>
          </div>
          <p className="text-sm text-white/60">
            Rung katalogiga o'z Telegram kanalingizni joylang va reytingda ko'taring.
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Turi: Faqat kanal */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
              Turi
            </label>
            <div className="flex items-center justify-between px-4 py-3 bg-white/[0.04] border border-white/10 rounded-xl">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#B8F03C]" />
                <span className="text-sm font-semibold text-white">Telegram Kanal</span>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-full bg-[#B8F03C]/10 text-[#B8F03C] font-medium border border-[#B8F03C]/20">
                Faqat kanal
              </span>
            </div>
          </div>
          
          {/* Handle */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
              Kanal manzili (Username yoki Link) <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 font-mono text-sm">
                @
              </span>
              <input 
                type="text" 
                value={handle.startsWith('@') ? handle.slice(1) : handle}
                onChange={e => setHandle(e.target.value.replace(/^@/, ''))}
                placeholder="masalan: rung_uz yoki t.me/rung_uz"
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl pl-9 pr-4 py-3 text-sm text-white placeholder-white/30 outline-none transition-all focus:border-[#B8F03C] focus:bg-white/[0.07]"
                required
              />
            </div>
          </div>
          
          {/* Nomi */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
              Kanal nomi <span className="text-red-400">*</span>
            </label>
            <input 
              type="text" 
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Masalan: Rung Rasmiy Kanali"
              className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/30 outline-none transition-all focus:border-[#B8F03C] focus:bg-white/[0.07]"
              required
            />
          </div>

          {/* Kategoriya - Custom Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
              Kategoriya <span className="text-red-400">*</span>
            </label>
            
            <button
              type="button"
              onClick={() => setIsCategoryOpen(!isCategoryOpen)}
              className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-left flex items-center justify-between text-sm transition-all hover:bg-white/[0.06] focus:border-[#B8F03C] outline-none"
              style={{
                borderColor: isCategoryOpen ? '#B8F03C' : undefined
              }}
            >
              {selectedCategoryObj ? (
                <span className="flex items-center gap-2.5 text-white font-medium">
                  <span>{selectedCategoryObj.icon}</span>
                  <span>{selectedCategoryObj.name_uz}</span>
                </span>
              ) : (
                <span className="text-white/40">Kategoriyani tanlang...</span>
              )}
              <svg 
                className={`w-4 h-4 text-white/50 transition-transform duration-200 ${isCategoryOpen ? 'rotate-180 text-[#B8F03C]' : ''}`}
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {isCategoryOpen && (
              <div 
                className="absolute left-0 right-0 top-full mt-2 z-50 bg-[#181B20] border border-white/15 rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto"
                style={{
                  boxShadow: '0 16px 36px rgba(0,0,0,0.6)'
                }}
              >
                {isCategoriesLoading ? (
                  <div className="p-4 text-center text-xs text-white/50">Kategoriyalar yuklanmoqda...</div>
                ) : categories && categories.length > 0 ? (
                  <div className="p-1.5 space-y-0.5">
                    {categories.map((cat: any) => {
                      const isSelected = cat.slug === category;
                      return (
                        <button
                          key={cat.slug}
                          type="button"
                          onClick={() => {
                            setCategory(cat.slug);
                            setIsCategoryOpen(false);
                          }}
                          className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm transition-colors text-left ${
                            isSelected 
                              ? 'bg-[#B8F03C]/15 text-[#B8F03C] font-semibold' 
                              : 'text-white/90 hover:bg-white/[0.08] hover:text-white'
                          }`}
                        >
                          <span className="flex items-center gap-2.5">
                            <span className="text-base">{cat.icon}</span>
                            <span>{cat.name_uz}</span>
                          </span>
                          {isSelected && (
                            <svg className="w-4 h-4 text-[#B8F03C]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="p-4 text-center text-xs text-white/50">Kategoriyalar topilmadi.</div>
                )}
              </div>
            )}
          </div>
          
          {/* Tavsifi */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
              Kanal tavsifi <span className="text-white/40 lowercase">(ixtiyoriy)</span>
            </label>
            <textarea 
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Kanal haqida qisqacha ma'lumot (mavzusi, maqsadi)..."
              rows={3}
              className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/30 outline-none transition-all focus:border-[#B8F03C] focus:bg-white/[0.07] resize-none"
            />
          </div>
          
          {/* Submit Button */}
          <div className="pt-2 flex items-center gap-3">
            <button 
              type="button"
              onClick={onClose}
              className="flex-1 py-3 px-4 rounded-xl border border-white/10 text-white/80 hover:text-white hover:bg-white/5 font-semibold text-sm transition-all"
            >
              Bekor qilish
            </button>
            <button 
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 py-3 px-4 rounded-xl bg-[#B8F03C] hover:bg-[#c6fa4d] active:scale-[0.98] text-[#0D0F11] font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#B8F03C]/20"
            >
              {mutation.isPending ? 'Qo\'shilmoqda...' : 'Kanalni qo\'shish'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
