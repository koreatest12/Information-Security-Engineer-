import { Server, Activity } from 'lucide-react';

export default function Dashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-6">System Status</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-ops-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/20 text-blue-400 rounded-lg"><Server /></div>
            <div>
              <p className="text-slate-400">Server Status</p>
              <h3 className="text-2xl font-bold text-white">Online</h3>
            </div>
          </div>
        </div>
        <div className="bg-ops-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500/20 text-green-400 rounded-lg"><Activity /></div>
            <div>
              <p className="text-slate-400">Uptime</p>
              <h3 className="text-2xl font-bold text-white">99.9%</h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}