import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  LayoutDashboard, Package, Truck, ShoppingCart, FileBarChart, LogOut,
  ChevronLeft
} from 'lucide-react';
import { useAuth } from '../../contexts';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/productos', icon: Package, label: 'Productos' },
  { to: '/proveedores', icon: Truck, label: 'Proveedores' },
  { to: '/ventas', icon: ShoppingCart, label: 'Ventas' },
  { to: '/reportes', icon: FileBarChart, label: 'Reportes' },
];

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { user, logout } = useAuth();

  return (
    <>
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex items-center justify-between px-4 h-16 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center text-sm font-bold text-gray-900 shadow-lg shadow-amber-500/25">
              IS
            </div>
            <div>
              <div className="text-sm font-bold text-gray-900 dark:text-white">
                Inven<span className="text-amber-500">Soft</span>
              </div>
              <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Gestión de Inventarios</div>
            </div>
          </div>
          <button
            onClick={onToggle}
            className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="text-[10px] font-mono uppercase tracking-widest text-gray-400 dark:text-gray-500 px-3 mb-2 mt-2 flex items-center gap-2">
            Principal
            <span className="flex-1 h-px bg-gray-200 dark:bg-gray-800" />
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={() => window.innerWidth < 1024 && onToggle()}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white border border-transparent'
              )}
            >
              <item.icon className="w-4.5 h-4.5" />
              {item.label}
            </NavLink>
          ))}

          
        </nav>

        <div className="p-3 border-t border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center text-xs font-bold text-gray-900">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-gray-900 dark:text-white truncate">
                {user?.first_name || user?.username || 'Usuario'}
              </p>
              <p className="text-[10px] font-mono text-gray-500 dark:text-gray-400 truncate">
                {user?.is_staff ? 'admin' : 'operador'}
              </p>
            </div>
            <button
              onClick={logout}
              title="Cerrar sesión"
              className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 text-gray-400 hover:text-red-500 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={onToggle}
        />
      )}
    </>
  );
}
