import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Newspaper,
  Mail,
  BarChart3,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useNewsletter } from '@/hooks'

const navItems = [
  {
    title: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    title: 'News',
    href: '/news',
    icon: Newspaper,
  },
  {
    title: 'Newsletter',
    href: '/newsletter',
    icon: Mail,
    showBadge: true,
  },
  {
    title: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
  },
]

export function Sidebar() {
  const { data: newsletter } = useNewsletter()
  const selectedCount = newsletter?.selected_count ?? 0

  return (
    <aside className="fixed left-0 top-14 z-40 h-[calc(100vh-3.5rem)] w-64 border-r bg-background">
      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.title}
            {item.showBadge && selectedCount > 0 && (
              <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
                {selectedCount}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
