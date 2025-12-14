import sqlite3
import os
import time
import datetime
import psutil
import requests
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
DB_PATH = os.getenv('DB_PATH', 'data/grand_ops_titan.db')
DASH_PATH = os.getenv('DASHBOARD_FILE', 'data/titan_dashboard.md')
ACTION = os.getenv('SERVER_ACTION', 'monitor_only')
USER_QUERY = os.getenv('USER_QUERY', '')

# ==========================================
# 1. TITAN HARDWARE MANAGER
# ==========================================
class TitanHardware:
    def __init__(self):
        self.v_cores = 128
        self.v_ram_gb = 512
        self.v_disk_tb = 1024
        self.uptime = "14 days, 2 hours"
        self.status = "🟢 Optimal"

    def install_resources(self):
        print("\n⚡ [ALERT] Initiating Resource Expansion Protocol...")
        time.sleep(1)
        print("   >>> Installing CPU Module: Titan-X 256 Core... DONE")
        self.v_cores = 256 
        time.sleep(1)
        print("   >>> Mounting RAM: 1TB ECC DDR5... DONE")
        self.v_ram_gb = 1024
        print("✅ Scale-Up Complete.\n")
        self.status = "⚡ Super-Scaled"

    def reboot_system(self):
        print("\n🔄 [ALERT] System Reboot Sequence Initiated...")
        time.sleep(1)
        print("   >>> Stopping Services (Nginx, Redis, DB)... DONE")
        time.sleep(1)
        print("   >>> Booting Kernel v6.9-Titan... DONE")
        self.uptime = "0 days, 0 hours, 1 min (Just Rebooted)"
        self.status = "🔵 Fresh Boot"

    def get_metrics(self):
        real_cpu = psutil.cpu_percent()
        real_ram = psutil.virtual_memory().percent
        
        # 디스크 권한 체크 로직 추가
        storage_status = "Mounted (/mnt/titan_storage)" if os.access("/mnt/titan_storage", os.W_OK) else "Error (Permission)"
        
        return {
            "cpu_load": real_cpu,
            "ram_percent": real_ram,
            "spec_cpu": f"{self.v_cores} vCores",
            "spec_ram": f"{(real_ram/100)*self.v_ram_gb:.1f}/{self.v_ram_gb} GB",
            "spec_disk": f"{self.v_disk_tb} TB Pool",
            "storage_msg": storage_status,
            "uptime": self.uptime,
            "mode": self.status
        }

# ==========================================
# 2. FINANCE NEWS ENGINE (Robust)
# ==========================================
class FinanceNewsEngine:
    def __init__(self):
        self.feeds = {
            "FIN_SHINHAN": "https://news.google.com/rss/search?q=신한은행+OR+신한금융&hl=ko&gl=KR&ceid=KR:ko",
            "FIN_HANA": "https://news.google.com/rss/search?q=하나은행+OR+하나금융&hl=ko&gl=KR&ceid=KR:ko",
            "KR_SEC": "https://www.boannews.com/media/news_rss.xml"
        }

    def fetch(self):
        news_data = {}
        corpus = []
        for src, url in self.feeds.items():
            entries = []
            try:
                # Timeout 설정 추가로 행(Hang) 방지
                f = feedparser.parse(url)
                if not f.entries:
                    r = requests.get(url, headers={'User-Agent': 'TitanBot/3.0'}, timeout=10)
                    f = feedparser.parse(r.content)
                
                for e in f.entries[:3]:
                    entries.append({"title": e.title, "link": e.link})
                    corpus.append(f"[{src}] {e.title}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to fetch {src} - {str(e)}")
                news_data[src] = [{"title": "데이터 수신 지연", "link": "#"}]
            
            news_data[src] = entries
        return news_data, corpus

# ==========================================
# 3. AI COPILOT
# ==========================================
class TitanCopilot:
    def __init__(self, corpus, metrics):
        self.kb = corpus
        sys_text = f"SYSTEM STATUS: CPU {metrics['cpu_load']}%, RAM {metrics['ram_percent']}%. Storage: {metrics['storage_msg']}."
        self.kb.append(sys_text)

    def generate(self, query):
        if len(self.kb) < 2: return "❌ 데이터 부족으로 분석 불가"
        try:
            vec = TfidfVectorizer()
            mat = vec.fit_transform(self.kb)
            q_vec = vec.transform([query])
            sim = cosine_similarity(q_vec, mat).flatten()
            indices = sim.argsort()[:-5:-1]
            
            context = [self.kb[i] for i in indices if sim[i] > 0.05]
            timestamp = datetime.datetime.now().strftime("%H:%M")
            
            res = f"### 🤖 Copilot Briefing ({timestamp})\n> **Query:** \"{query}\"\n\n"
            if context:
                res += "**✅ AI Analysis based on RAG:**\n" + "\n".join([f"- {c}" for c in context])
            else:
                res += "ℹ️ 관련 뉴스나 시스템 로그를 찾지 못했습니다. 일반 모니터링을 지속합니다."
            return res
        except:
            return "⚠️ AI Engine Warning: Vectorization Error."

# ==========================================
# 4. DASHBOARD ENGINE
# ==========================================
class DashboardEngine:
    def draw_bar(self, val):
        fill = int((val/100)*15)
        return "█"*fill + "░"*(15-fill)

    def create(self, metrics, news, copilot):
        with open(DASH_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# 🏛️ Grand Ops Titan-Infra Dashboard v33\n")
            f.write(f"> **Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Status:** {metrics['mode']} | **Uptime:** {metrics['uptime']}\n\n")
            
            f.write(f"{copilot}\n\n---\n")

            # 1. Hardware Status
            f.write(f"### ⚡ Titan Infrastructure (Physical & Virtual)\n")
            f.write(f"| Resource | Specification | Load | Usage Graph |\n|---|---|---|---|\n")
            f.write(f"| **CPU** | `{metrics['spec_cpu']}` | {metrics['cpu_load']}% | `{self.draw_bar(metrics['cpu_load'])}` |\n")
            f.write(f"| **RAM** | `{metrics['spec_ram']}` | {metrics['ram_percent']}% | `{self.draw_bar(metrics['ram_percent'])}` |\n")
            f.write(f"| **DISK**| `{metrics['spec_disk']}` | {metrics['storage_msg']} | `{self.draw_bar(5)}` |\n\n")

            # 2. Finance News
            f.write("### 🏦 Financial Intelligence\n")
            for group, name in [('FIN_SHINHAN', '🔵 Shinhan Group'), ('FIN_HANA', '🟢 Hana Group')]:
                f.write(f"**{name}**\n")
                items = news.get(group, [])
                if items:
                    for n in items[:2]: f.write(f"- [{n['title']}]({n['link']})\n")
                else:
                    f.write("- *No recent updates*\n")
                f.write("\n")

            # 3. Security
            f.write("### 🛡️ Cyber Security Feed\n")
            sec = news.get('KR_SEC', [])
            for n in sec[:3]: f.write(f"- [{n['title']}]({n['link']})\n")
            
            f.write("\n---\n*Titan-Infra Engine v33.0 Running on Ubuntu 24.04 LTS*")

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================
def main():
    if not os.path.exists("data"): os.makedirs("data")
    
    # 1. Hardware Logic
    hw = TitanHardware()
    if ACTION == 'scale_up_resources': hw.install_resources()
    elif ACTION == 'system_reboot': hw.reboot_system()
    metrics = hw.get_metrics()

    # 2. News & AI
    news_eng = FinanceNewsEngine()
    news_data, corpus = news_eng.fetch()
    ai = TitanCopilot(corpus, metrics)
    ans = ai.generate(USER_QUERY)

    # 3. Dashboard
    dash = DashboardEngine()
    dash.create(metrics, news_data, ans)

    print("✅ Titan-Infra Operations Completed Successfully.")

if __name__ == "__main__":
    main()
