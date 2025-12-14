import os
import json

# =======================================================
# ⚛️ REACT CORE GENERATOR (Grand Ops Edition)
# =======================================================
FRONTEND_DIR = "frontend"
SRC_DIR = os.path.join(FRONTEND_DIR, "src")
PUBLIC_DIR = os.path.join(FRONTEND_DIR, "public")

def create_file(path, content):
    """파일 생성 헬퍼 함수"""
    try:
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ Generated: {path}")
    except Exception as e:
        print(f"❌ Error generating {path}: {e}")

def generate_react_ecosystem():
    print("🚀 Initializing Grand Ops React Ecosystem...")

    # 1. package.json (최신 의존성 및 보안 설정)
    package_json = {
        "name": "grand-ops-frontend",
        "private": True,
        "version": "10.5.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
            "preview": "vite preview",
            "security-audit": "npm audit --audit-level=high"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "axios": "^1.6.0",
            "recharts": "^2.10.0",
            "framer-motion": "^10.16.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.43",
            "@types/react-dom": "^18.2.17",
            "@vitejs/plugin-react": "^4.2.1",
            "eslint": "^8.55.0",
            "eslint-plugin-react": "^7.33.2",
            "eslint-plugin-react-hooks": "^4.6.0",
            "eslint-plugin-react-refresh": "^0.4.5",
            "vite": "^5.0.8"
        }
    }
    create_file(os.path.join(FRONTEND_DIR, "package.json"), json.dumps(package_json, indent=2))

    # 2. Vite Config (보안 헤더 및 포트 설정)
    vite_config = """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true,
    headers: {
      'X-Frame-Options': 'DENY',
      'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline';",
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
    """
    create_file(os.path.join(FRONTEND_DIR, "vite.config.js"), vite_config)

    # 3. Main Entry (index.html)
    index_html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Grand Ops Secure Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
    """
    create_file(os.path.join(FRONTEND_DIR, "index.html"), index_html)

    # 4. Source Code - Entry (main.jsx)
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

    # 5. Source Code - CSS (index.css)
    index_css = """
:root { font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; }
body { margin: 0; display: flex; place-items: center; min-width: 320px; min-height: 100vh; }
.dashboard { padding: 2rem; border: 1px solid #1e293b; border-radius: 12px; background: #1e293b; width: 100%; max-width: 800px; }
h1 { color: #38bdf8; }
.status-ok { color: #4ade80; font-weight: bold; }
    """
    create_file(os.path.join(SRC_DIR, "index.css"), index_css)

    # 6. Source Code - App Component (App.jsx)
    app_jsx = """
import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState('Initializing...')

  useEffect(() => {
    // Simulate API Check
    setTimeout(() => setStatus('SECURE & OPERATIONAL'), 1500)
  }, [])

  return (
    <div className="dashboard">
      <h1>🚀 Grand Ops Control Center</h1>
      <p>System Status: <span className="status-ok">{status}</span></p>
      <hr style={{borderColor: '#334155'}}/>
      <p>Security Level: <strong>MAXIMUM</strong></p>
      <p>React Engine: <strong>v18.2.0 (Active)</strong></p>
    </div>
  )
}

export default App
    """
    create_file(os.path.join(SRC_DIR, "App.jsx"), app_jsx)

    # 7. Git Ignore (Frontend specific)
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
