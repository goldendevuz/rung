
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { About } from './pages/About';
import { Rules } from './pages/Rules';
import { Kategoriyalar } from './pages/Kategoriyalar';

// Dummy components for other pages until we implement them
const Kunlik = () => (
  <section id="page-kunlik">
    <div className="wrap">
      <div className="page-head">
        <h1>Kunlik taxtalar</h1>
        <p>Har kun yarim tunda (Toshkent vaqti) taxta yopiladi va yangisi 1 B dan boshlanadi. Yopilgan kun natijalari shu yerda qoladi.</p>
      </div>
      <div className="daycards" id="dayCards">
        <p>API integratsiyasi jarayonda...</p>
      </div>
    </div>
  </section>
);

const AddChannel = () => (
  <section id="page-qoshish">
    <div className="wrap">
      <div className="page-head">
        <h1>Kanal qo'shish</h1>
        <p>Avval kanal ro'yxatga tushadi, keyin egaligi tasdiqlanadi. Faqat tasdiqlangan egalar o'rin sotib oladi.</p>
      </div>
      <div className="board" style={{ paddingTop: '22px' }}>
        <p>Tez kunda...</p>
      </div>
    </div>
  </section>
);

const Login = () => <div className="wrap"><br/><h1>Kirish sahifasi</h1></div>;
const Listing = () => <div className="wrap"><br/><h1>Kanal Sahifasi</h1></div>;
const NotFound = () => <div className="wrap"><br/><h1>Sahifa topilmadi (404)</h1></div>;

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
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
            <Route path="/p/:slug" element={<Listing />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
