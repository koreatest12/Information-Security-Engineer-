import { Outlet, Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-ops-900">
      <aside className="w-64 border-r border-ops-800 p-6">
        <div className="flex items-center gap-2 mb-8 text-white font-bold text-xl">
          <Shield className="text-ops-500" /> Grand Ops
        </div>
        <nav className="space-y-2">
          <Link to="/" className="block px-4 py-2 bg-ops-800 rounded text-white">Dashboard</Link>
        </nav>
      </aside>
      <main className="flex-1 p-8"><Outlet /></main>
    </div>
  );
}