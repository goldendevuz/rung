import { BrowserRouter, Routes, Route } from 'react-router-dom'

function HomePage() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Manrope, sans-serif' }}>
      <h1>Rung</h1>
      <p>Bir pog&apos;ona yuqoriga. \U0001FA9C</p>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<HomePage />} />
        <Route path="/p/:slug" element={<HomePage />} />
        <Route path="*" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
