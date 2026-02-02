import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryProvider } from '@/providers/QueryProvider'
import { MainLayout } from '@/components/layout'
import { Dashboard, NewsList, Newsletter, Analytics } from '@/pages'

function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/news" element={<NewsList />} />
            <Route path="/newsletter" element={<Newsletter />} />
            <Route path="/analytics" element={<Analytics />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryProvider>
  )
}

export default App
