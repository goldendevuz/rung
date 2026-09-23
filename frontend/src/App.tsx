
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { About } from './pages/About';
import { Rules } from './pages/Rules';
import { Kategoriyalar } from './pages/Kategoriyalar';
import { Login } from './pages/Login';
import { Profile } from './pages/Profile';
import { AddChannel } from './pages/AddChannel';
import { Listing } from './pages/Listing';
import { Wallet } from './pages/Wallet';
import { Statistika } from './pages/Statistika';
import { Kunlik } from './pages/Kunlik';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';

// Dummy components for other pages until we implement them


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
        <ToastProvider>
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
                <Route path="/profil" element={<Profile />} />
                <Route path="/hamyon" element={<Wallet />} />
                <Route path="/wallet" element={<Wallet />} />
                <Route path="/statistika" element={<Statistika />} />
                <Route path="/p/:id" element={<Listing />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
