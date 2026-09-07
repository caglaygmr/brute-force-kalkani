from flask import Flask, request, render_template_string, session, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "super_gizli_anahtar_kimse_bilmesin" # Oturum (session) yönetimi için zorunlu

# --- Basit kullanıcı veritabanı ---
USERS = {
    "admin": "secret123",
}

# --- Log dosyası ayarları ---
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "login.log")
os.makedirs(LOG_DIR, exist_ok=True)

def log_attempt(ip, username, success):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "SUCCESS" if success else "FAIL"
    line = f"{ts}  IP={ip}  user={username}  result={result}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

# --- GİRİŞ SAYFASI HTML ---
LOGIN_PAGE = """
<!doctype html>
<meta charset="utf-8">
<title>Giriş</title>
<style>
  body{font-family:sans-serif;background:#0f1311;color:#e7ebe7;display:grid;place-items:center;height:100vh;margin:0}
  form{background:#161b18;padding:28px;border-radius:12px;border:1px solid #28302b;width:280px}
  input{width:100%;padding:10px;margin:6px 0;box-sizing:border-box;border-radius:8px;border:1px solid #3a443d;background:#0f1311;color:#e7ebe7}
  button{width:100%;padding:10px;margin-top:10px;border:0;border-radius:8px;background:#1f8a70;color:#fff;font-weight:600;cursor:pointer}
  .msg{margin-top:12px;font-size:.9rem}
  .no{color:#f07567}
</style>
<form method="post">
  <h2>🔐 Giriş</h2>
  <input name="username" placeholder="Kullanıcı adı" autocomplete="off">
  <input name="password" type="password" placeholder="Parola" autocomplete="off">
  <button>Giriş yap</button>
  {% if msg %}<div class="msg no">{{ msg }}</div>{% endif %}
</form>
"""

# --- DASHBOARD (PANO) SAYFASI HTML ---
DASHBOARD_PAGE = """
<!doctype html>
<meta charset="utf-8">
<title>Yönetim Paneli</title>
<style>
  body{font-family:sans-serif;background:#0f1311;color:#e7ebe7;padding:40px}
  .card{background:#161b18;padding:20px;border-radius:12px;border:1px solid #28302b; margin-bottom:20px; max-width: 600px;}
  .btn{display:inline-block; padding:8px 16px; background:#f07567; color:white; text-decoration:none; border-radius:6px;}
  /* DİKKAT: Gizli verileri CSS ile ekrandan saklıyoruz */
  .secret-data { display: none; } 
</style>

<h1>🛒 Şirket İçi Ürün Paneli</h1>
<p>Hoş geldin, sistem yöneticisi.</p>

<div class="card">
    <h3>📦 Aktif Ürünler</h3>
    <ul>
        <li>Standart Sunucu Paketi - $50</li>
        <li>Premium Güvenlik Duvarı - $120</li>
        <li>Yıllık Log Analiz Lisansı - $200</li>
    </ul>
</div>

<!-- CTF İPUCU: Gizli ürün kataloğu veritabanından çekilemediği için geçici olarak HTML içine gömüldü. -->
<div class="secret-data">
    <h3>🔥 GİZLİ VERİLER (SATIŞA KAPALI)</h3>
    <p>Tebrikler! Başarılı bir şekilde sisteme sızdın ve kaynak kodları inceledin.</p>
    <ul>
        <li><strong>FLAG_1 (Kişi A için görev):</strong> FLAG{BRUTE_FORCE_ILE_ICERI_SIZILDI}</li>
        <li><strong>Sızdırılmış API Anahtarı:</strong> xk9_8f92a4b_admin_token</li>
    </ul>
</div>

<a href="/logout" class="btn">Sistemden Çıkış Yap</a>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        ip = request.remote_addr

        success = USERS.get(username) == password
        log_attempt(ip, username, success)

        if success:
            # Şifre doğruysa oturum aç ve dashboard'a yönlendir
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            msg = "Kullanıcı adı veya parola hatalı."
            
    return render_template_string(LOGIN_PAGE, msg=msg)

@app.route("/dashboard")
def dashboard():
    # Sadece giriş yapmış (session'ı olan) kişiler bu sayfayı görebilir
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_PAGE)

@app.route("/logout")
def logout():
    # Çıkış yapıldığında oturumu sil ve login sayfasına at
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def index():
    return redirect(url_for('login'))

if __name__ == "__main__":
    print("Hedef login calisiyor:  http://localhost:5000/login")
    app.run(host="0.0.0.0", port=5000, debug=False)