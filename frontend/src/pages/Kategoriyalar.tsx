import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchCategories } from '../api/client';

export function Kategoriyalar() {
  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories
  });

  return (
    <section id="page-kategoriyalar">
      <div className="wrap">
        <div className="page-head">
          <h1>Kategoriyalar</h1>
          <p>Reklama beruvchilar kanalni mavzusi bo'yicha qidiradi. Har bir kategoriyaning o'z reytingi bor.</p>
        </div>
        
        {isLoading && <p>Yuklanmoqda...</p>}
        
        {!isLoading && (
          <div className="catgrid" id="catGrid">
            {categories.map((c: any) => (
              <div className="catcard" key={c.slug}>
                <h3><span className="sq" style={{ '--c': c.color } as any}></span>{c.name}</h3>
                <p className="cnt">0 kanal</p>
                {/* Normally we'd show the top 3 channels here, but API doesn't return that yet */}
                <button 
                  className="btn-ghost" 
                  style={{ width: '100%', fontSize: '13.5px', minHeight: '40px' }}
                >
                  1 B ga birinchi bo'ling
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
