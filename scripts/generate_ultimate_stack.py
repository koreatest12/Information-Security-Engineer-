import os, json

BASE = os.getcwd()
FRONT = os.path.join(BASE, "frontend")
SERVER = os.path.join(BASE, "backend_server")

def write(path, content):
    d = os.path.dirname(path)
    if not os.path.exists(d): os.makedirs(d)
    with open(path, "w", encoding="utf-8") as f: f.write(content.strip())
    print(f"✅ Created: {path}")

def gen_root_config():
    # 루트 gitignore 최적화
    gitignore = """
node_modules
dist
.env
.DS_Store
coverage
# 데이터 폴더는 무시하되 DB는 허용
data/*
!data/*.db
!data/*.sql
"""
    write(os.path.join(BASE, ".gitignore"), gitignore)

def gen_frontend():
    # Package.json
    pkg = {
        "name": "grand-ops-pro", "private": True, "version": "3.1.0", "type": "module",
        "scripts": { "dev": "vite", "build": "vite build", "lint": "eslint ." },
        "dependencies": {
            "react": "^18.2.0", "react-dom": "^18.2.0", "react-router-dom": "^6.20.0",
            "axios": "^1.6.2", "framer-motion": "^10.16.0", "recharts": "^2.10.0",
            "lucide-react": "^0.294.0", "clsx": "^2.0.0", "tailwind-merge": "^2.1.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.43", "@vitejs/plugin-react": "^4.2.1",
            "autoprefixer": "^10.4.16", "postcss": "^8.4.32", "tailwindcss": "^3.3.6",
            "vite": "^5.0.8", "eslint": "^8.55.0"
        }
    }
    write(os.path.join(FRONT, "package.json"), json.dumps(pkg, indent=2))
    
    # Configs
    write(os.path.join(FRONT, "vite.config.js"), "import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react'; import path from 'path'; export default defineConfig({ plugins: [react()], resolve: { alias: { '@': path.resolve(__dirname, './src') } }, build: { outDir: 'dist', emptyOutDir: true } });")
    write(os.path.join(FRONT, "tailwind.config.js"), "export default { content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'], theme: { extend: { colors: { ops: { 900:'#0f172a', 800:'#1e293b', 500:'#0ea5e9' } } } }, plugins: [] }")
    write(os.path.join(FRONT, "postcss.config.js"), "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }")
    
    # HTML & Main
    write(os.path.join(FRONT, "index.html"), "<!doctype html><html lang='en'><head><meta charset='UTF-8'/><title>Grand Ops System</title></head><body class='bg-ops-900 text-white'><div id='root'></div><script type='module' src='/src/main.jsx'></script></body></html>")
    write(os.path.join(FRONT, "src/main.jsx"), "import React from 'react'; import ReactDOM from 'react-dom/client'; import { BrowserRouter } from 'react-router-dom'; import App from './App'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><BrowserRouter><App /></BrowserRouter></React.StrictMode>);")
    write(os.path.join(FRONT, "src/index.css"), "@tailwind base; @tailwind components; @tailwind utilities;")
    
    # App & Components
    write(os.path.join(FRONT, "src/App.jsx"), """
import { Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './Dashboard';
export default function App() { return (<Routes><Route path="/" element={<Layout />}><Route index element={<Dashboard />} /></Route></Routes>); }
""")
    
    write(os.path.join(FRONT, "src/Layout.jsx"), """
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
""")
    
    write(os.path.join(FRONT, "src/Dashboard.jsx"), """
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
const data = [{v:40},{v:30},{v:60},{v:50},{v:80},{v:70}];
export default function Dashboard() {
   return (
     <div>
       <h2 className="text-2xl font-bold mb-6">System Status: <span className="text-green-500">OPTIMAL</span></h2>
       <div className="h-64 bg-ops-800 rounded border border-slate-700 p-4">
         <ResponsiveContainer width="100%" height="100%">
           <AreaChart data={data}><Area type="monotone" dataKey="v" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.2} /></AreaChart>
         </ResponsiveContainer>
       </div>
     </div>
   )
}
""")

def gen_server():
    pkg = { "name": "server", "version": "1.0.0", "type": "module", "scripts": { "start": "node server.js" }, "dependencies": { "express": "^4.18.2", "cors": "^2.8.5", "helmet": "^7.1.0" } }
    write(os.path.join(SERVER, "package.json"), json.dumps(pkg, indent=2))
    write(os.path.join(SERVER, "server.js"), """
import express from 'express'; import path from 'path'; import { fileURLToPath } from 'url';
const app = express(); const PORT = process.env.PORT || 5000;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
app.use(express.static(path.join(__dirname, '../frontend/dist')));
app.get('*', (req, res) => res.sendFile(path.join(__dirname, '../frontend/dist/index.html')));
app.listen(PORT, () => console.log('Server Ready'));
""")

if __name__ == "__main__":
    gen_root_config()
    gen_frontend()
    gen_server()
