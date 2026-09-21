import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

export const Listing = () => {
  const { slug } = useParams<{ slug: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ['listing', slug],
    queryFn: async () => {
      const res = await fetch(`/api/v1/listings/${slug}`);
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error('Not Found');
        }
        throw new Error('Server Error');
      }
      return res.json();
    },
    retry: false,
  });

  if (isLoading) {
    return (
      <section id="page-listing">
        <div className="wrap">
          <br />
          <p>Yuklanmoqda...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="page-listing">
        <div className="wrap">
          <br />
          <h1>Kanal topilmadi</h1>
          <p>Bunday kanal mavjud emas.</p>
        </div>
      </section>
    );
  }

  return (
    <section id="page-listing">
      <div className="wrap">
        <br />
        <div className="card">
          <h1>{data.name}</h1>
          <p className="rdesc">{data.description}</p>
          <div className="rmeta" style={{ marginTop: '14px' }}>
            <span className="sq" style={{ background: data.category?.color || 'var(--ink-3)' }}></span>
            <b>{data.category?.name_uz || 'Kategoriya'}</b>
            <span className="sep">·</span>
            {data.subscribers?.toLocaleString('ru-RU')} obunachi
          </div>
          <br />
          <a
            href={data.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
            style={{ display: 'inline-flex', alignItems: 'center', textDecoration: 'none' }}
          >
            Kanalga o'tish
          </a>
        </div>
      </div>
    </section>
  );
};
