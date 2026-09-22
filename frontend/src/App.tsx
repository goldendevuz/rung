
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { About } from './pages/About';
import { Rules } from './pages/Rules';
import { Kategoriyalar } from './pages/Kategoriyalar';
import { Login } from './pages/Login';
import { AddChannel } from './pages/AddChannel';
import { Listing } from './pages/Listing';
import { AuthProvider } from './contexts/AuthContext';

// Dummy components for other pages until we implement them
const Kunlik = () => (
  <section id="page-kunlik">
    <div className="wrap">
      <div className="page-head">
        <h1>Kunlik taxtalar</h1>
        <p>Har kun yarim tunda (Toshkent vaqti) taxta yopiladi va yangisi 1 B dan boshlanadi. Yopilgan kun natijalari shu yerda qoladi.</p>
      </div>
      <div className="daycards" id="dayCards">
        <p className="empty-state">Hali yopilgan kunlik reyting yo'q</p>
      </div>
    </div>
  </section>
);

const NotFound = () => (
  <section id="page-404">
    <div className="wrap">
      <br/>
      <h1>Sahifa topilmadi (404)</h1><p>Siz qidirayotgan sahifa topilmadi. Ehtimol, manzil xato kiritilgandir yoki bu sahifa olib tashlangan bolishi mumkin. Asosiy sahifaga qaytib, boshqa bolimlarni korib chiqing yoki qidiruvdan foydalaning.</p>
    </div>
  </section>
);

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/kunlik" element={<Kunlik />} />
              <Route path="/kategoriyalar" element={<Kategoriyalar />} />
              <Route path="/qoshish" element={<AddChannel />} />
              <Route path="/haqida" element={<About />} />
              <Route path="/qoidalar" element={<Rules />} />
              <Route path="/kirish" element={<Login />} />
              <Route path="/login" element={<Login />} />
              <Route path="/p/:id" element={<Listing />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
