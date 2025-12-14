import json
import os
import time
import datetime
import psutil
import requests
import feedparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
STATE_PATH = os.getenv('STATE_FILE', 'data/titan_status.json')
DASH_PATH = os.getenv('DASHBOARD_FILE', 'data/titan_dashboard.md')
ACTION = os.getenv('SERVER_ACTION', 'monitor_only')
REPO = os.getenv('REPO_NAME', '')
USER_QUERY = os.getenv('USER_QUERY', '')

# ==========================================
# 1. TITAN HARDWARE MANAGER (With Persistence)
# ==========================================
class TitanHardware:
    def __init__(self):
        self.state = self.load_state()
        
    def load_state(self):
        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH, 'r') as f:
                    return json.load(f)
            except: pass
        # 초기 상태 (Factory Default)
        return {
            "v_cores": 128,
            "v_ram_gb": 512,
            "v_disk_tb": 1024,
            "last_boot": time.time(),
            "status": "🟢 Optimal",
            "generation": 1
        }

    def save_state(self):
        with open(STATE_PATH, 'w') as f:
            json.dump(self.state, f, indent=4)

    def process_action(self, action_cmd):
        if action_cmd == 'scale_up_resources':
            print("\n⚡ [ACTION] Scaling Up Resources...")
            self.state['v_cores'] *= 2
            self.state['v_ram_gb'] *= 2
            self.state['status'] = "⚡ Scaled-Up"
            self.state['generation'] += 1
            
        elif action_cmd == 'system_reboot':
            print("\n🔄 [ACTION] Rebooting System...")
            self.state['last_boot'] = time.time()
            self.state['status'] = "🔵 Fresh Boot"

        elif action_cmd == 'reset_factory':
            if os.path.exists(STATE_PATH):
                os.remove(STATE_PATH)
            self.__init__() # Reload default
        
        self.save_state()

    def get_metrics(self):
        uptime_sec = time.time() - self.state['last_boot']
        uptime_str = str(datetime.timedelta(seconds=int(uptime_sec)))
        
        real_cpu = psutil.cpu_percent()
        real_ram = psutil.virtual_memory().percent
        
        return {
            "cpu_load": real_cpu,
            "ram_percent": real_ram,
            "spec_cpu": f"{self.state['v_cores']} vCores",
            "spec_ram": f"{(real_ram/100)*self.state['v_ram_gb']:.1f}/{self.state['v_ram_gb']} GB",
            "spec_disk": f"{self.state['v_disk_tb']} TB",
            "uptime": uptime_str,
            "mode": self.state['status'],
            "gen": self.state['generation']
        }

# ==========================================
# 2. FINANCE NEWS ENGINE
# ==========================================
class FinanceNewsEngine:
    def fetch(self):
        feeds = {
            "FIN_SHINHAN": "https://news.google.com/rss/search?q=신한금융&hl=ko&gl=KR&ceid=KR:ko",
            "KR_ECON": "https://news.google.com/rss/search?q=한국경제&hl=ko&gl=KR&ceid=KR:ko"
        }
        news_data = {}
        corpus = []
        for src, url in feeds.items():
            entries = []
            try:
                f = feedparser.parse(url)
                if not f.entries:
                    r = requests.get(url, headers={'User-Agent': 'Bot'}, timeout=5)
                    f = feedparser.parse(r.content)
                for e in f.entries[:2]:
                    entries.append({"title": e.title, "link": e.link})
                    corpus.append(f"[{src}] {e.title}")
            except: 
                news_data[src] = [{"title": "News Feed Error", "link": "#"}]
            news_data[src] = entries
        return news_data, corpus

# ==========================================
# 3. AI COPILOT
# ==========================================
class TitanCopilot:
    def __init__(self, corpus, metrics):
        self.kb = corpus
        self.kb.append(f"SYS: CPU {metrics['spec_cpu']}, RAM {metrics['spec_ram']}, Mode {metrics['mode']}")

    def generate(self, query):
        if len(self.kb) < 2: return "데이터 부족"
        try:
            vec = TfidfVectorizer()
            mat = vec.fit_transform(self.kb)
            q_vec = vec.transform([query])
            sim = cosine_similarity(q_vec, mat).flatten()
            idx = sim.argsort()[:-3:-1]
            ctx = [self.kb[i] for i in idx if sim[i] > 0.05]
            
            res = f"> **Q:** {query}\n\n"
            res += "**🤖 AI Analysis:**\n" + "\n".join([f"- {c}" for c in ctx]) if ctx else "관련 정보 없음"
            return res
        except: return "AI Engine Error"

# ==========================================
# 4. DASHBOARD ENGINE (Control Center)
# ==========================================
class DashboardEngine:
    def draw_bar(self, val):
        fill = int((val/100)*15)
        return "█"*fill + "░"*(15-fill)

    def create(self, metrics, news, copilot):
        action_url = f"https://github.com/{REPO}/actions/workflows/main.yml"
        
        with open(DASH_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# 🏛️ Grand Ops Titan-Infra Control Center\n")
            f.write(f"> **Status:** {metrics['mode']} (Gen {metrics['gen']}) | **Uptime:** {metrics['uptime']}\n\n")
            
            # 배지 버튼 영역
            f.write("### 🎮 Operations Control Center\n")
            f.write("시스템 제어가 필요하면 아래 버튼을 클릭하여 **Run workflow**를 실행하십시오.\n\n")
            f.write(f"[![Reboot](https://img.shields.io/badge/COMMAND-SYSTEM__REBOOT-red?style=for-the-badge&logo=linux&logoColor=white)]({action_url}) ")
            f.write(f"[![ScaleUp](https://img.shields.io/badge/COMMAND-SCALE__UP-blue?style=for-the-badge&logo=server&logoColor=white)]({action_url}) ")
            f.write(f"[![Reset](https://img.shields.io/badge/COMMAND-FACTORY__RESET-grey?style=for-the-badge&logo=github&logoColor=white)]({action_url})\n\n")
            
            f.write(f"{copilot}\n\n---\n")

            f.write(f"### ⚡ Hardware Metrics\n")
            f.write(f"| Resource | Spec | Usage | Graph |\n|---|---|---|---|\n")
            f.write(f"| **CPU** | `{metrics['spec_cpu']}` | {metrics['cpu_load']}% | `{self.draw_bar(metrics['cpu_load'])}` |\n")
            f.write(f"| **RAM** | `{metrics['spec_ram']}` | {metrics['ram_percent']}% | `{self.draw_bar(metrics['ram_percent'])}` |\n\n")

            f.write("### 🏦 Financial Briefing\n")
            for k, v in news.items():
                if v: f.write(f"- [{v[0]['title']}]({v[0]['link']})\n")
            
            f.write("\n---\n*Titan-Infra v35.0 Automated Dashboard*")

def main():
    if not os.path.exists("data"): os.makedirs("data")
    hw = TitanHardware()
    hw.process_action(ACTION)
    metrics = hw.get_metrics()

    news_eng = FinanceNewsEngine()
    news_data, corpus = news_eng.fetch()
    
    ai = TitanCopilot(corpus, metrics)
    ans = ai.generate(USER_QUERY)

    dash = DashboardEngine()
    dash.create(metrics, news_data, ans)
    print("✅ Operation Complete.")

if __name__ == "__main__":
    main()
