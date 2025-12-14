import os
import json
import sys

# =======================================================
# ⚛️ REACT CORE GENERATOR (Grand Ops Edition V2)
# =======================================================
FRONTEND_DIR = "frontend"
SRC_DIR = os.path.join(FRONTEND_DIR, "src")
PUBLIC_DIR = os.path.join(FRONTEND_DIR, "public")
ASSETS_DIR = os.path.join(SRC_DIR, "assets")

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

def create_file(path, content):
    """파일 생성 (덮어쓰기 방지 로직 제거 - 강제 동기화 위함)"""
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ Generated/Updated: {path}")
    except Exception as e:
        print(f"❌ Error generating {path}: {e}")

def generate_react_ecosystem():
    print("🚀 Initializing Grand Ops React Ecosystem V2...")
    
    ensure_dir(FRONTEND_DIR)
    ensure_dir(SRC_DIR)
    ensure_dir(PUBLIC_DIR)
    ensure_dir(ASSETS_DIR)

    # 1. package.json (캐시 최적화를 위해 버전 명시)
    package_json = {
        "name": "grand-ops-frontend",
        "private": True,
        "version": "1.0.0",
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
            "axios": "^1.6.2",
            "lucide-react": "^0.294.0",
            "clsx": "^2.0.0",
            "tailwind-merge": "^2.1.0"
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
            "eslint-plugin-react-hooks": "^4.6.0",
            "eslint-plugin-react-refresh": "^0.4.5",
            "vite": "^5.0.8"
        }
    }
    create_file(os.path.join(FRONTEND_DIR, "package.json"), json.dumps(package_json, indent=2))

    # 2. Vite Config
    vite_config = """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
})
    """
    create_file(os.path.join(FRONTEND_DIR, "vite.config.js"), vite_config)

    # 3. Tailwind Config (스타일링 대량 추가 대비)
    tailwind_config = """
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
    """
    create_file(os.path.join(FRONTEND_DIR, "tailwind.config.js"), tailwind_config)
    
    # 4. PostCSS Config
    postcss_config = """
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
    """
    create_file(os.path.join(FRONTEND_DIR, "postcss.config.js"), postcss_config)

    # 5. Entry Files
    index_html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Grand Ops Dashboard</title>
  </head>
  <body class="bg-slate-950 text-white">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
    """
    create_file(os.path.join(FRONTEND_DIR, "index.html"), index_html)

    # 6. Source Files
    main_jsx = """
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
    """
    create_file(os.path.join(SRC_DIR, "main.jsx"), main_jsx)

    index_css = """
@tailwind base;
@tailwind components;
@tailwind utilities;

body { font-family: 'Inter', sans-serif; }
    """
    create_file(os.path.join(SRC_DIR, "index.css"), index_css)

    app_jsx = """
import { useState, useEffect } from 'react'

function App() {
  const [systemTime, setSystemTime] = useState(new Date().toISOString());

  useEffect(() => {
    const timer = setInterval(() => setSystemTime(new Date().toISOString()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl">
        <h1 className="text-2xl font-bold text-blue-500 mb-4">🛡️ Grand Ops Security</h1>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-3 bg-slate-800 rounded">
            <span className="text-slate-400">System Status</span>
            <span className="text-green-400 font-mono font-bold">OPERATIONAL</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-slate-800 rounded">
             <span className="text-slate-400">Current Time</span>
             <span className="text-xs text-slate-300 font-mono">{systemTime}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
    """
    create_file(os.path.join(SRC_DIR, "App.jsx"), app_jsx)

    # 7. GitIgnore
    gitignore = """
node_modules
dist
.env
.DS_Store
coverage
    """
    create_file(os.path.join(FRONTEND_DIR, ".gitignore"), gitignore)

if __name__ == "__main__":
    generate_react_ecosystem()
