import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function MainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Sidebar />
      <main className="pl-64 pt-14">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
