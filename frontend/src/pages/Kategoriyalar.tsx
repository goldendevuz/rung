
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
        {!isLoading && categories.length === 0 && (
          <p className="empty-state">Hali kategoriyalar qo'shilmagan</p>
        )}
        
        {!isLoading && categories.length > 0 && (
          <div className="catgrid" id="catGrid">
            {categories.map((c: any) => (
              <div className="catcard" key={c.slug}>
                <h3>
                  {c.icon ? <span style={{ marginRight: '6px' }}>{c.icon}</span> : <span className="sq" style={{ '--c': c.color } as any} />}
                  {c.name_uz || c.name}
                </h3>
                <p className="cnt">{c.listing_count || 0} kanal</p>
                <a 
                  href={`/?category=${c.slug}`}
                  className="btn-ghost" 
                  style={{ width: '100%', fontSize: '13px', minHeight: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                >
                  {c.listing_count === 0
                    ? "1 B ga birinchi bo'ling"
                    : `${c.next_rank_price_b ?? 1} B ga 1-o'rinni oling`}
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
