"""
Hedef Sistem — Profesyonel Kurumsal Yönetim & Güvenlik Paneli
KİŞİ B (Savunma Tarafı)
"""

from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
from datetime import datetime
import os

app = Flask(__name__)
# Güvenli oturum anahtarı
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aegis_core_enterprise_secret_key_2026")

# --- Kullanıcı Veritabanı ---
USERS = {
    "admin": "secret123",
    "operator": "ops2026!",
}

# --- Log Ayarları (detector.py ile %100 uyumlu) ---
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "login.log")
os.makedirs(LOG_DIR, exist_ok=True)

def log_attempt(ip, username, success):
    """Giriş denemelerini tespit motorunun okuyacağı standart formatta kaydeder."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "SUCCESS" if success else "FAIL"
    line = f"{ts}  IP={ip}  user={username}  result={result}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"[{result}] {ts} - IP: {ip} - User: {username}")

# ==============================================================================
# 🎨 1. GİRİŞ SAYFASI (MODERN GLASSMORPHIC LOGIN)
# ==============================================================================
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aegis Core // Güvenli Giriş Portalı</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .glass-panel {
      background: rgba(17, 24, 39, 0.75);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
  
  <!-- Arka Plan Işık Efektleri -->
  <div class="absolute -top-40 -left-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
  <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>

  <div class="w-full max-w-md relative z-10">
    <!-- Logo & Başlık -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/20 mb-4">
        <div class="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
          <svg class="w-7 h-7 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
        </div>
      </div>
      <h1 class="text-2xl font-bold tracking-tight text-white">AEGIS CORE</h1>
      <p class="text-xs font-medium text-slate-400 mt-1 uppercase tracking-widest">Kurumsal Sunucu Yönetim Sistemi</p>
    </div>

    <!-- Giriş Kartı -->
    <div class="glass-panel p-8 rounded-2xl shadow-2xl">
      <form method="POST" class="space-y-5">
        <div>
          <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Kullanıcı Adı</label>
          <div class="relative">
            <input type="text" name="username" required autofocus autocomplete="off"
                   placeholder="admin"
                   class="w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition duration-200">
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider">Erişim Parolası</label>
            <span class="text-[11px] text-slate-500">SSO Aktif</span>
          </div>
          <div class="relative">
            <input type="password" name="password" required autocomplete="off"
                   placeholder="••••••••••••"
                   class="w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition duration-200">
          </div>
        </div>

        {% if msg %}
        <div class="p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-xs animate-shake">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span>{{ msg }}</span>
        </div>
        {% endif %}

        <button type="submit" 
                class="w-full py-3.5 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-semibold text-sm rounded-xl shadow-lg shadow-emerald-500/20 active:scale-[0.99] transition duration-200 flex items-center justify-center gap-2">
          <span>Sisteme Kimlik Doğrula</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </button>
      </form>

      <div class="mt-6 pt-6 border-t border-slate-800 text-center">
        <p class="text-[11px] text-slate-500">
          🔒 Uçtan uca şifrelenmiş tünel bağlantısı (TLS 1.3 / Port 5000)
        </p>
      </div>
    </div>
  </div>
</body>
</html>
"""

# ==============================================================================
# 📊 2. DASHBOARD (KURUMSAL SAAS & SOC İZLEME PANELİ)
# ==============================================================================
DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aegis Core // Yönetim Konsolu</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex">

  <!-- Sol Menü (Sidebar) -->
  <aside class="w-64 bg-slate-900/60 border-r border-slate-800/80 p-5 flex flex-col justify-between hidden md:flex">
    <div>
      <div class="flex items-center gap-3 px-2 mb-8">
        <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
          🛡️
        </div>
        <div>
          <h2 class="text-sm font-bold tracking-tight text-white leading-tight">AEGIS OS</h2>
          <span class="text-[10px] text-emerald-400 font-mono">v3.4.2-ENTERPRISE</span>
        </div>
      </div>

      <nav class="space-y-1">
        <button onclick="switchTab('overview')" id="tab-btn-overview" class="tab-btn w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          Sistem Özeti & Node'lar
        </button>

        <button onclick="switchTab('products')" id="tab-btn-products" class="tab-btn w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/50 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
          Kurumsal Ürün Kataloğu
        </button>

        <!-- ZAFİYET / CTF ALANI: Profesyonelce gizlenmiş Teşhis & Debug Sekmesi -->
        <button onclick="switchTab('diagnostics')" id="tab-btn-diagnostics" class="tab-btn w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-amber-400/80 hover:text-amber-300 hover:bg-amber-500/10 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
          Sistem Teşhis & Vault
        </button>
      </nav>
    </div>

    <!-- Alt Profil & Oturum Kapatma -->
    <div class="pt-4 border-t border-slate-800/80">
      <div class="flex items-center justify-between mb-3 px-1">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
            AD
          </div>
          <div>
            <div class="text-xs font-semibold text-white">admin@root</div>
            <div class="text-[10px] text-emerald-400">Super Administrator</div>
          </div>
        </div>
      </div>
      <a href="/logout" class="w-full flex items-center justify-center gap-2 py-2 px-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded-lg text-xs font-semibold border border-rose-500/20 transition">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
        Oturumu Kapat
      </a>
    </div>
  </aside>

  <!-- Ana İçerik Alanı -->
  <main class="flex-1 flex flex-col min-w-0 overflow-y-auto">
    <!-- Üst Bar -->
    <header class="h-16 border-b border-slate-800/80 px-8 flex items-center justify-between bg-slate-900/30 backdrop-blur">
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
          Canlı Savunma Aktif
        </span>
        <span class="text-xs text-slate-400">IP: {{ request.remote_addr }}</span>
      </div>
      <div class="text-xs text-slate-400 font-mono">
        Hedef Port: <span class="text-emerald-400">5000</span>
      </div>
    </header>

    <div class="p-8 max-w-6xl w-full">

      <!-- ================= TAB 1: SİSTEM ÖZETİ ================= -->
      <div id="content-overview" class="tab-content space-y-6">
        <div>
          <h1 class="text-xl font-bold text-white tracking-tight">Kurumsal Altyapı ve Güvenlik Durumu</h1>
          <p class="text-xs text-slate-400 mt-0.5">Sistem metrikleri, aktif savunma servisleri ve sunucu yük dağılımı.</p>
        </div>

        <!-- İstatistik Kartları -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Mikroservisler</div>
            <div class="text-2xl font-bold text-white mt-2">12 / 12</div>
            <div class="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">✓ Tüm servisler stabil</div>
          </div>

          <div class="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Kalkan Durumu (IDS)</div>
            <div class="text-2xl font-bold text-emerald-400 mt-2">Dinlemede</div>
            <div class="text-[11px] text-slate-400 mt-1">login.log aktif akıyor</div>
          </div>

          <div class="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Aktif Oturum</div>
            <div class="text-2xl font-bold text-cyan-400 mt-2">1 (Admin)</div>
            <div class="text-[11px] text-slate-400 mt-1">Oturum süresi: 30 dk</div>
          </div>

          <div class="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Uptime</div>
            <div class="text-2xl font-bold text-white mt-2">99.98%</div>
            <div class="text-[11px] text-slate-400 mt-1">Son 30 gün kesintisiz</div>
          </div>
        </div>

        <!-- Node Listesi -->
        <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
            <h3 class="text-xs font-bold text-white uppercase tracking-wider">Aktif Savunma & Servis Düğümleri</h3>
            <span class="text-[11px] text-slate-400">Son senkronizasyon: Şimdi</span>
          </div>
          <div class="divide-y divide-slate-800/60 text-xs">
            <div class="px-6 py-3.5 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span class="font-medium text-white">auth-gateway-primary (Flask Web Target)</span>
              </div>
              <span class="font-mono text-slate-400">127.0.0.1:5000</span>
              <span class="text-emerald-400 font-semibold">ONLINE</span>
            </div>
            <div class="px-6 py-3.5 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span class="font-medium text-white">shield-detector-daemon (Kişi B Motoru)</span>
              </div>
              <span class="font-mono text-slate-400">target/logs/login.log</span>
              <span class="text-emerald-400 font-semibold">WATCHING</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= TAB 2: ÜRÜN VE HİZMETLER ================= -->
      <div id="content-products" class="tab-content hidden space-y-6">
        <div>
          <h1 class="text-xl font-bold text-white tracking-tight">Kurumsal Lisans & Ürün Kataloğu</h1>
          <p class="text-xs text-slate-400 mt-0.5">Şirket içi satın alınmış aktif güvenlik paketleri.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <span class="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">INFRA</span>
              <h3 class="text-base font-bold text-white mt-2">Standart Sunucu Node Paketi</h3>
              <p class="text-xs text-slate-400 mt-2">8 vCPU, 32GB RAM kapasiteli izole saldırı hedef sunucusu.</p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
              <span class="text-lg font-bold text-white">$50 <span class="text-xs font-normal text-slate-400">/ ay</span></span>
              <span class="text-xs text-emerald-400 font-medium">Aktif</span>
            </div>
          </div>

          <div class="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <span class="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">SECURITY</span>
              <h3 class="text-base font-bold text-white mt-2">Brute-Force Kalkanı (WAF/IPS)</h3>
              <p class="text-xs text-slate-400 mt-2">Sliding window algoritmalı gerçek zamanlı IP kilit mekanizması.</p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
              <span class="text-lg font-bold text-white">$120 <span class="text-xs font-normal text-slate-400">/ ay</span></span>
              <span class="text-xs text-emerald-400 font-medium">Aktif</span>
            </div>
          </div>

          <div class="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <span class="text-[10px] font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">ANALYTICS</span>
              <h3 class="text-base font-bold text-white mt-2">SOC Log Analiz Lisansı</h3>
              <p class="text-xs text-slate-400 mt-2">Otomatik eşik tespiti ve çoklu iş parçacığı saldırı uyarısı.</p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
              <span class="text-lg font-bold text-white">$200 <span class="text-xs font-normal text-slate-400">/ yıl</span></span>
              <span class="text-xs text-emerald-400 font-medium">Aktif</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= TAB 3: ZAFİYET & TEŞHİS VAULT (CTF ALANI) ================= -->
      <div id="content-diagnostics" class="tab-content hidden space-y-6">
        <div class="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex items-start gap-3">
          <svg class="w-5 h-5 text-amber-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          <div>
            <h3 class="text-xs font-bold text-amber-300 uppercase tracking-wider">⚠️ Geliştirici & Sistem Yöneticisi Teşhis Paneli</h3>
            <p class="text-xs text-amber-200/80 mt-1">
              Bu panel üretim ortamında (Production) kapalı olmalıdır. Yanlış konfigürasyon sonucu hassas ortam değişkenleri sızdırılmıştır.
            </p>
          </div>
        </div>

        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">⚙️ Yüklenmiş Ortam Değişkenleri (Environment Dump)</h3>
          
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 space-y-2 overflow-x-auto">
            <div class="text-slate-500"># --- OTOMATİK OLUŞTURULAN TEŞHİS ÇIKTISI ---</div>
            <div><span class="text-cyan-400">SYSTEM_ENV</span>=<span class="text-emerald-400">"production_us_east"</span></div>
            <div><span class="text-cyan-400">DEBUG_MODE</span>=<span class="text-rose-400">True</span> <span class="text-slate-500"># UYARI: Kapatılması unutuldu!</span></div>
            <div><span class="text-cyan-400">DB_CONNECTION</span>=<span class="text-slate-300">"postgresql://admin:***@10.0.4.12:5432/core_db"</span></div>
            <div class="pt-2 border-t border-slate-800/80">
              <span class="text-amber-400 font-bold">CTF_FLAG_KEY</span>=<span class="text-amber-300 font-bold">"FLAG{BRUTE_FORCE_EXPLOIT_SUCCESS_2026}"</span>
            </div>
            <div>
              <span class="text-purple-400">INTERNAL_MASTER_API_TOKEN</span>=<span class="text-purple-300">"aegis_sec_994a8f23b7e01dc5"</span>
            </div>
          </div>

          <div class="text-[11px] text-slate-400">
            🎯 <strong>Saldırgan (Kişi A) için Not:</strong> Brute-Force ile admin parolasını (`secret123`) kırıp bu panele erişerek sistem bayrağını (FLAG) ve Master API anahtarını ele geçirdiniz!
          </div>
        </div>
      </div>

    </div>
  </main>

  <script>
    function switchTab(tabId) {
      // Tüm içerikleri gizle
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      // Tüm buton stillerini sıfırla
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-emerald-500/10', 'text-emerald-400', 'border', 'border-emerald-500/20');
        btn.classList.add('text-slate-400');
      });

      // Seçilen tabı göster
      const content = document.getElementById('content-' + tabId);
      if (content) content.classList.remove('hidden');

      // Seçilen butonu aktifleştir
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) {
        activeBtn.classList.remove('text-slate-400');
        activeBtn.classList.add('bg-emerald-500/10', 'text-emerald-400', 'border', 'border-emerald-500/20');
      }
    }
  </script>
</body>
</html>
"""

# ==============================================================================
# 🚀 ROUTE TANIMLARI
# ==============================================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        ip = request.remote_addr

        success = USERS.get(username) == password
        log_attempt(ip, username, success)

        if success:
            session['logged_in'] = True
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            msg = "Geçersiz kimlik bilgileri. Erişim denemesi kaydedildi."
            
    return render_template_string(LOGIN_PAGE, msg=msg)

@app.route("/dashboard")
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_PAGE)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def index():
    return redirect(url_for('login'))

if __name__ == "__main__":
    print("==================================================")
    print("🛡️  AEGIS CORE - HEDEF SUNUCU ÇALIŞIYOR")
    print("🌐  URL : http://localhost:5000/login")
    print("📁  LOG :", os.path.abspath(LOG_FILE))
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)