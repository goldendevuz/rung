import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchCategories, createListing, uploadLogo, fetchCandidates } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { cleanTelegramHandle } from '../utils/formatters';

interface AddListingModalProps {
  onClose: () => void;
}

export default function AddListingModal({ onClose }: AddListingModalProps) {
  const { user, mutate: refreshUser } = useAuth();
  const toast = useToast();
  const queryClient = useQueryClient();

  // Wizard step: 1 = Channel details, 2 = Pick target rank
  const [step, setStep] = useState<1 | 2>(1);

  // Step 1 fields
  const [kind] = useState('channel');
  const [handle, setHandle] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [logoPreview, setLogoPreview] = useState('');
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Step 2 fields
  const [targetRank, setTargetRank] = useState<number>(1);

  const { data: categories, isLoading: isCategoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  });

  const { data: candidates = [], isLoading: isCandidatesLoading } = useQuery({
    queryKey: ['candidates', 'all_time'],
    queryFn: () => fetchCandidates('all_time', 10),
    enabled: step === 2,
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

  const handleLogoChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error("Faqat rasm fayllari (PNG, JPG, WebP) qabul qilinadi.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error("Rasm hajmi 5 MB dan oshmasligi kerak.");
      return;
    }

    const preview = URL.createObjectURL(file);
    setLogoPreview(preview);
    setIsUploadingLogo(true);

    try {
      const res = await uploadLogo(file);
      setLogoUrl(res.url);
    } catch (err: any) {
      toast.error(err.message || "Logotip yuklashda xatolik yuz berdi");
      setLogoPreview('');
      setLogoUrl('');
    } finally {
      setIsUploadingLogo(false);
    }
  };

  const handleRemoveLogo = () => {
    setLogoUrl('');
    setLogoPreview('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const selectedCategoryObj = categories?.find((c: any) => c.slug === category);

  const selectedCandidate = candidates.find((c) => c.rank === targetRank);
  const requiredCost = selectedCandidate ? selectedCandidate.price_b : 1;
  const currentBalance = user?.balance ?? 0;
  const isInsufficient = currentBalance < requiredCost;
  const deficit = Math.max(0, requiredCost - currentBalance);

  const mutation = useMutation({
    mutationFn: createListing,
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['myListings'] });
      queryClient.invalidateQueries({ queryKey: ['board'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      queryClient.invalidateQueries({ queryKey: ['tabs'] });
      refreshUser();
      const rankNum = data.target_rank || targetRank;
      toast.success(`Kanal muvaffaqiyatli qo'shildi va #${rankNum}-o'ringa joylashtirildi!`);
      onClose();
    },
    onError: (err: any) => {
      toast.error(err.message || 'Xatolik yuz berdi');
    }
  });

  const handleProceedToStep2 = (e: React.FormEvent) => {
    e.preventDefault();
    if (!handle.trim() || !name.trim() || !category) {
      toast.error("Iltimos, barcha kerakli maydonlarni to'ldiring.");
      return;
    }
    refreshUser();
    setStep(2);
  };

  const handleFinalSubmit = () => {
    const clean = cleanTelegramHandle(handle);
    mutation.mutate({
      kind,
      handle: clean || handle.trim(),
      name: name.trim(),
      description: description.trim(),
      category_slug: category,
      claim_now: true,
      target_rank: targetRank,
      period_type: 'all_time',
      logo_url: logoUrl || undefined
    });
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in overflow-y-auto"
      style={{ animation: 'fadeIn 0.15s ease-out' }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div 
        className="w-full max-w-lg bg-[#12151A] border border-white/10 rounded-2xl p-6 sm:p-8 shadow-2xl relative my-8"
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
        
        {/* Header with Step Indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-xl">{step === 1 ? '📢' : '🎯'}</span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                {step === 1 ? "Yangi kanal qo'shish" : "O'rinni tanlang"}
              </h2>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-white/10 text-white/70 font-semibold">
              Bosqich {step} / 2
            </span>
          </div>
          <p className="text-sm text-white/60">
            {step === 1 
              ? "Kanal ma'lumotlarini kiriting va keyingi bosqichda reytingdagi o'rinni tanlang."
              : "Reytingdan o'zingiz xohlagan o'rinni tanlang. Band o'rinlar 1 pog'ona pastga suriladi."}
          </p>
          {step === 1 && (
            <div className="mt-3 p-2.5 rounded-xl bg-white/[0.04] border border-white/10 text-xs text-white/70 flex gap-2">
              <span className="text-[#B8F03C]">💡</span>
              <p>
                <b>Eslatma:</b> Real vaqtli o'sish statistikasini ko'rish uchun, kanalni qo'shgandan so'ng <b>@rung_uz_bot</b>'ni kanalingizga admin qiling.
              </p>
            </div>
          )}
        </div>

        {step === 1 ? (
          <form onSubmit={handleProceedToStep2} className="space-y-4">
            {/* Turi */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-1.5">
                Turi
              </label>
              <div className="flex items-center justify-between px-3.5 py-2.5 bg-white/[0.04] border border-white/10 rounded-xl">
                <div className="flex items-center gap-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#B8F03C]" />
                  <span className="text-sm font-semibold text-white">Telegram Kanal</span>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#B8F03C]/10 text-[#B8F03C] font-medium border border-[#B8F03C]/20">
                  Faqat kanal
                </span>
              </div>
            </div>
            
            {/* Handle */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-1.5">
                Kanal manzili (Username yoki Link) <span className="text-red-400">*</span>
              </label>
              <div className="relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/40 font-mono text-sm">
                  @
                </span>
                <input 
                  type="text" 
                  value={handle.startsWith('@') ? handle.slice(1) : handle}
                  onChange={e => setHandle(e.target.value.replace(/^@/, ''))}
                  placeholder="masalan: rung_uz yoki t.me/rung_uz"
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl pl-8 pr-4 py-2.5 text-sm text-white placeholder-white/30 outline-none transition-all focus:border-[#B8F03C] focus:bg-white/[0.07]"
                  required
                />
              </div>
            </div>
            
            {/* Nomi */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-1.5">
                Kanal nomi <span className="text-red-400">*</span>
              </label>
              <input 
                type="text" 
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Masalan: Rung Rasmiy Kanali"
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-white/30 outline-none transition-all focus:border-[#B8F03C] focus:bg-white/[0.07]"
                required
              />
            </div>

            {/* Kanal logotipi */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-1.5">
                Kanal logotipi <span className="text-white/40 lowercase font-normal">(ixtiyoriy)</span>
              </label>
              <input 
                type="file" 
                ref={fileInputRef}
                onChange={handleLogoChange}
                accept="image/png, image/jpeg, image/webp, image/gif"
                className="hidden"
              />

              {logoPreview ? (
                <div className="flex items-center gap-3 p-2.5 bg-white/[0.04] border border-white/10 rounded-xl">
                  <div className="relative w-10 h-10 rounded-lg overflow-hidden bg-white/5 border border-white/10 flex-shrink-0">
                    <img src={logoPreview} alt="Logo preview" className="w-full h-full object-cover" />
                    {isUploadingLogo && (
                      <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                        <div className="w-4 h-4 border-2 border-[#B8F03C] border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-white truncate">
                      {isUploadingLogo ? "Logotip yuklanmoqda..." : "Logotip yuklandi ✓"}
                    </p>
                    <p className="text-[11px] text-white/50">PNG, JPG, WebP (512px WebP ga optimallanadi)</p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="text-xs px-2.5 py-1 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
                    >
                      O'zgartirish
                    </button>
                    <button
                      type="button"
                      onClick={handleRemoveLogo}
                      className="text-xs px-2 py-1 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full flex items-center justify-center gap-3 p-3 bg-white/[0.03] border border-dashed border-white/20 hover:border-[#B8F03C]/50 hover:bg-white/[0.05] rounded-xl transition-all cursor-pointer group text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-white/60 group-hover:text-[#B8F03C] group-hover:bg-[#B8F03C]/10 transition-colors flex-shrink-0">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white/80 group-hover:text-white transition-colors">
                      Logotip yuklash uchun bosing
                    </p>
                    <p className="text-[11px] text-white/40">
                      Yuklanmasa, avtomatik Telegram avataridan olinadi
                    </p>
                  </div>
                </button>
              )}
            </div>

            {/* Kategoriya - Custom Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-1.5">
                Kategoriya <span className="text-red-400">*</span>
              </label>
              
              <button
                type="button"
                onClick={() => setIsCategoryOpen(!isCategoryOpen)}
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-3.5 py-2.5 text-left flex items-center justify-between text-sm transition-all hover:bg-white/[0.06] focus:border-[#B8F03C] outline-none"
                style={{
                  borderColor: isCategoryOpen ? '#B8F03C' : undefined
                }}
              >
                {selectedCategoryObj ? (
                  <span className="flex items-center gap-2 text-white font-medium">
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
                  className="absolute left-0 right-0 top-full mt-1.5 z-50 bg-[#181B20] border border-white/15 rounded-xl shadow-2xl overflow-hidden max-h-52 overflow-y-auto"
                  style={{ boxShadow: '0 16px 36px rgba(0,0,0,0.6)' }}
                >
                  {isCategoriesLoading ? (
                    <div className="p-3 text-center text-xs text-white/50">Kategoriyalar yuklanmoqda...</div>
                  ) : categories && categories.length > 0 ? (
                    <div className="p-1 space-y-0.5">
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
                            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors text-left ${
                              isSelected 
                                ? 'bg-[#B8F03C]/15 text-[#B8F03C] font-semibold' 
                                : 'text-white/90 hover:bg-white/[0.08] hover:text-white'
                            }`}
                          >
                            <span className="flex items-center gap-2">
                              <span>{cat.icon}</span>
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
                    <div className="p-3 text-center text-xs text-white/50">Kategoriyalar topilmadi.</div>
                  )}
                </div>
              )}
            </div>
            
            {/* Tavsifi */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-1.5">
                Kanal tavsifi <span className="text-white/40 lowercase">(ixtiyoriy)</span>
              </label>
              <textarea 
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Kanal haqida qisqacha ma'lumot (mavzusi, maqsadi)..."
                rows={2}
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-3.5 py-2 text-sm text-white placeholder-white/30 outline-none transition-all focus:border-[#B8F03C] focus:bg-white/[0.07] resize-none"
              />
            </div>
            
            {/* Step 1 Actions */}
            <div className="pt-3 flex items-center gap-3">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 py-3 px-4 rounded-xl border border-white/10 text-white/80 hover:text-white hover:bg-white/5 font-semibold text-sm transition-all"
              >
                Bekor qilish
              </button>
              <button 
                type="submit"
                className="flex-1 py-3 px-4 rounded-xl bg-[#B8F03C] hover:bg-[#c6fa4d] active:scale-[0.98] text-[#0D0F11] font-bold text-sm transition-all shadow-lg shadow-[#B8F03C]/20"
              >
                Keyingi: O'rinni tanlash →
              </button>
            </div>
          </form>
        ) : (
          /* Step 2: Pick Target Rank */
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
                Qaysi o'ringa joylashmoqchisiz?
              </label>
              
              {isCandidatesLoading ? (
                <div className="p-6 text-center text-sm text-white/50 bg-white/[0.03] rounded-xl border border-white/10">
                  O'rinlar va jonli narxlar tekshirilmoqda...
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-2 max-h-56 overflow-y-auto pr-1">
                  {candidates.map((c) => {
                    const isSelected = c.rank === targetRank;
                    return (
                      <button
                        key={c.rank}
                        type="button"
                        onClick={() => setTargetRank(c.rank)}
                        className={`p-3 rounded-xl border text-left transition-all relative ${
                          isSelected
                            ? 'bg-[#B8F03C]/10 border-[#B8F03C] shadow-md shadow-[#B8F03C]/10'
                            : 'bg-white/[0.03] border-white/10 hover:border-white/20 hover:bg-white/[0.05]'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                            isSelected ? 'bg-[#B8F03C] text-[#0D0F11]' : 'bg-white/10 text-white'
                          }`}>
                            #{c.rank}
                          </span>
                          <span className="text-sm font-extrabold text-[#B8F03C]">
                            {c.price_b} B
                          </span>
                        </div>
                        <div className="text-[11px] truncate text-white/70">
                          {c.is_occupied ? (
                            <span>Band: <b className="text-white/90">{c.holder_name || c.holder_handle}</b></span>
                          ) : (
                            <span className="text-[#B8F03C]/80">✨ Bo'sh o'rin</span>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Summary card */}
            <div className="p-4 rounded-xl bg-white/[0.04] border border-white/10 space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-white/70">Tanlangan o'rin:</span>
                <span className="font-bold text-white">#{targetRank}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/70">O'rin narxi:</span>
                <span className="font-bold text-[#B8F03C]">{requiredCost} B</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/70">Joriy balansingiz:</span>
                <span className="font-medium text-white">{currentBalance.toLocaleString()} B</span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-white/10">
                <span className="text-white/70">To'lovdan so'ng:</span>
                <span className="font-bold text-white">
                  {isInsufficient ? '-' : `${(currentBalance - requiredCost).toLocaleString()} B`}
                </span>
              </div>
            </div>

            {isInsufficient && (
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex flex-col gap-1.5">
                <div className="font-bold flex items-center gap-1.5 text-amber-300">
                  <span>⚠️</span> Mablag' yetarli emas
                </div>
                <p className="leading-relaxed">
                  #{targetRank}-o'rinni olish uchun kamida <b>{requiredCost} B</b> kerak. Sizda <b>{currentBalance} B</b> mavjud (yetishmayapti: <b>{deficit} B</b>).
                </p>
              </div>
            )}

            {/* Step 2 Actions */}
            <div className="pt-2 flex items-center gap-3">
              <button 
                type="button"
                onClick={() => setStep(1)}
                className="py-3 px-4 rounded-xl border border-white/10 text-white/80 hover:text-white hover:bg-white/5 font-semibold text-sm transition-all"
              >
                ← Orqaga
              </button>

              {isInsufficient ? (
                <a
                  href={`/hamyon?amount=${deficit}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3 px-4 rounded-xl bg-[#B8F03C] hover:bg-[#c6fa4d] text-[#0D0F11] font-bold text-sm text-center flex items-center justify-center gap-2 shadow-lg shadow-[#B8F03C]/20 transition-all"
                  style={{ textDecoration: 'none' }}
                >
                  <span>💳</span> {deficit} B to'ldirish →
                </a>
              ) : (
                <button 
                  type="button"
                  disabled={mutation.isPending || isCandidatesLoading}
                  onClick={handleFinalSubmit}
                  className="flex-1 py-3 px-4 rounded-xl bg-[#B8F03C] hover:bg-[#c6fa4d] active:scale-[0.98] text-[#0D0F11] font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#B8F03C]/20"
                >
                  {mutation.isPending 
                    ? 'Qo\'shilmoqda...' 
                    : `${requiredCost} B to'lash va kanalni joylash`}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
