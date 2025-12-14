import os
import json
import sys

# =======================================================
# 🚀 GRAND OPS: ULTIMATE FULL-STACK GENERATOR (V9 Fixed)
# =======================================================
BASE_DIR = os.getcwd()
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
SERVER_DIR = os.path.join(BASE_DIR, "backend_server")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Created: {path}")

def create_file(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Generated: {path}")

def generate_root_gitignore():
    # 루트 레벨 gitignore (DB 파일 허용 명시)
    content = """
node_modules
dist
.env
.DS_Store
coverage
# Data 폴더는 무시하되, DB 파일은 강제로 허용 (!)
data/*
!data/*.db
!data/*.sql
"""
    create_file(os.path.join(BASE_DIR, ".gitignore"), content)

def generate_frontend():
    print("\n[1/2] ⚛️ Generating Expert React Ecosystem...")
    
    # 1. Package.json
    pkg = {
        "name": "grand-ops-client",
        "private": True,
        "version": "2.1.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.20.0",
            "axios": "^1.6.2",
            "framer-motion": "^10.16.5",
            "lucide-react": "^0.294.0",
            "clsx": "^2.0.0",
            "tailwind-merge": "^2.1.0",
            "recharts": "^2.10.3"
        },
        "devDependencies": {
            "@types/react": "^18.2.43",
            "@types/react-dom": "^18.2.17",
            "@vitejs/plugin-react": "^4.2.1",
            "autoprefixer": "^10.4.16",
            "postcss": "^8.4.32",
            "tailwindcss": "^3.3.6",
            "eslint": "^8.55.0",
            "eslint-plugin-react": "^7.33.2",
            "vite": "^5.0.8"
        }
    }
    create_file(os.path.join(FRONTEND_DIR, "package.json"), json.dumps(pkg, indent=2))

    # 2. Vite Config
    vite_conf = """
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    proxy: { '/api': 'http://localhost:5000' }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false
  }
});
"""
    create_file(os.path.join(FRONTEND_DIR, "vite.config.js"), vite_conf)

    # 3. Tailwind & PostCSS
    create_file(os.path.join(FRONTEND_DIR, "tailwind.config.js"), """
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: { ops: { 900: '#0f172a', 800: '#1e293b', 400: '#38bdf8', 500: '#0ea5e9' } }
    },
  },
  plugins: [],
}
""")
    create_file(os.path.join(FRONTEND_DIR, "postcss.config.js"), "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }")

    # 4. Entry Point & Source
    create_file(os.path.join(FRONTEND_DIR, "index.html"), """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Grand Ops Console</title>
  </head>
  <body class="bg-ops-900 text-slate-200">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""")

    create_file(os.path.join(FRONTEND_DIR, "src/main.jsx"), """
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
""")

    create_file(os.path.join(FRONTEND_DIR, "src/index.css"), """
@tailwind base;
@tailwind components;
@tailwind utilities;
body { font-family: 'Inter', sans-serif; }
""")

    # App.jsx
    create_file(os.path.join(FRONTEND_DIR, "src/App.jsx"), """
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
""")

    # Components
    create_file(os.path.join(FRONTEND_DIR, "src/components/Layout.jsx"), """
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
""")

    create_file(os.path.join(FRONTEND_DIR, "src/pages/Dashboard.jsx"), """
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
""")

def generate_backend_server():
    print("\n[2/2] 🛡️ Generating Node.js Server...")
    
    server_pkg = {
        "name": "grand-ops-server",
        "version": "1.0.0",
        "type": "module",
        "scripts": { "start": "node server.js" },
        "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5",
            "helmet": "^7.1.0",
            "compression": "^1.7.4"
        }
    }
    create_file(os.path.join(SERVER_DIR, "package.json"), json.dumps(server_pkg, indent=2))

    server_js = """
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 5000;

app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors());
app.use(compression());
app.use(express.json());

app.get('/api/health', (req, res) => res.json({ status: 'OK', system: 'Grand Ops' }));

const distPath = path.join(__dirname, '../frontend/dist');
app.use(express.static(distPath));
app.get('*', (req, res) => res.sendFile(path.join(distPath, 'index.html')));

app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
"""
    create_file(os.path.join(SERVER_DIR, "server.js"), server_js)

if __name__ == "__main__":
    generate_root_gitignore()
    generate_frontend()
    generate_backend_server()
    print("\n✅ Full-Stack Generation Complete.")
