import { Outlet } from 'react-router-dom';
import { Shield } from 'lucide-react';
export default function Layout() {
  return (
    <div className="flex h-screen bg-ops-900 text-white">
      <aside className="w-64 border-r border-ops-800 p-6">
        <h1 className="flex items-center gap-2 font-bold text-xl mb-8"><Shield className="text-ops-500"/> Grand Ops</h1>
        <div className="text-sm text-slate-500">System V3.1 Active</div>
      </aside>
      <main className="flex-1 p-8"><Outlet /></main>
    </div>
  )
}