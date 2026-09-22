import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchCategories, createListing } from '../api/client';

interface AddListingModalProps {
  onClose: () => void;
}

export default function AddListingModal({ onClose }: AddListingModalProps) {
  const [kind, setKind] = useState('channel');
  const [handle, setHandle] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const queryClient = useQueryClient();

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  });

  const mutation = useMutation({
    mutationFn: createListing,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-listings'] });
      onClose();
    },
    onError: (err: Error) => {
      alert(err.message);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!handle || !name || !category) {
      alert("Iltimos barcha kerakli maydonlarni to'ldiring.");
      return;
    }
    mutation.mutate({
      kind,
      handle,
      name,
      description,
      category_slug: category
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-[#121417] border border-white/10 rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto relative">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-white/50 hover:text-white"
        >
          ✕
        </button>
        
        <h2 className="text-xl font-semibold mb-6">Yangi qo'shish</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Turi</label>
            <select 
              value={kind} 
              onChange={e => setKind(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-[#B8F03C]"
            >
              <option value="channel">Kanal</option>
              <option value="group">Guruh</option>
              <option value="bot">Bot</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Handle (Username yoki Link)</label>
            <input 
              type="text" 
              value={handle}
              onChange={e => setHandle(e.target.value)}
              placeholder="@username yoki https://t.me/..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-[#B8F03C]"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Nomi</label>
            <input 
              type="text" 
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Masalan: Kodlash.uz"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-[#B8F03C]"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Kategoriya</label>
            <select 
              value={category} 
              onChange={e => setCategory(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-[#B8F03C]"
              required
            >
              <option value="">Kategoriyani tanlang</option>
              {categories?.map((cat: any) => (
                <option key={cat.slug} value={cat.slug}>{cat.icon} {cat.name_uz}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Tavsifi</label>
            <textarea 
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Kanal yoki guruhingiz haqida qisqacha ma'lumot..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-[#B8F03C] min-h-[100px]"
            />
          </div>
          
          <button 
            type="submit"
            disabled={mutation.isPending}
            className="w-full bg-[#B8F03C] hover:bg-[#a3d936] text-black font-semibold py-3 rounded-xl transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Qo\'shilmoqda...' : 'Qo\'shish'}
          </button>
        </form>
      </div>
    </div>
  );
}
