"""
Hedef Login Sistemi  —  KİŞİ B (savunma tarafı) bu dosyayı çalıştırır.

Görevi:
  1. Basit bir web login sayfası sunmak (/login)
  2. HER giriş denemesini bir log dosyasına yazmak (logs/login.log)

Çalıştırma:
    pip install flask
    python app.py
Sonra tarayıcıdan: http://localhost:5000

Aynı WiFi'deki diğer kişi (Kişi A) senin IP'ine bağlanır, örn:
    http://192.168.1.34:5000
IP'ni öğrenmek için: Windows -> ipconfig, Mac/Linux -> ifconfig veya ip a
"""

from flask import Flask, request, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# --- Basit kullanıcı veritabanı (şimdilik kod içinde) -----------------------
# Not: doğru parola "secret123" ve bu parola attacker/wordlist.txt içinde de var,
# böylece demo'da saldırı gerçekten "bulur".
USERS = {
    "admin": "secret123",
}

# --- Log dosyası ------------------------------------------------------------
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "login.log")
os.makedirs(LOG_DIR, exist_ok=True)


def log_attempt(ip, username, success):
    """Her giriş denemesini tek satır olarak log dosyasına ekler."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "SUCCESS" if success else "FAIL"
    line = f"{ts}  IP={ip}  user={username}  result={result}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    # Terminale de basalım ki KİŞİ B canlı görsün
    print(line.strip())


# --- Basit HTML login formu -------------------------------------------------
PAGE = """
<!doctype html>
<meta charset="utf-8">
<title>Giris</title>
<style>
  body{font-family:sans-serif;background:#0f1311;color:#e7ebe7;display:grid;
       place-items:center;height:100vh;margin:0}
  form{background:#161b18;padding:28px;border-radius:12px;border:1px solid #28302b;width:280px}
  h2{margin:0 0 16px}
  input{width:100%;padding:10px;margin:6px 0;box-sizing:border-box;border-radius:8px;
        border:1px solid #3a443d;background:#0f1311;color:#e7ebe7}
  button{width:100%;padding:10px;margin-top:10px;border:0;border-radius:8px;
         background:#1f8a70;color:#fff;font-weight:600;cursor:pointer}
  .msg{margin-top:12px;font-size:.9rem}
  .ok{color:#4fd0ac}.no{color:#f07567}
</style>
<form method="post">
  <h2>🔐 Giriş</h2>
  <input name="username" placeholder="Kullanıcı adı" autocomplete="off">
  <input name="password" type="password" placeholder="Parola" autocomplete="off">
  <button>Giriş yap</button>
  {% if msg %}<div class="msg {{ cls }}">{{ msg }}</div>{% endif %}
</form>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    msg, cls = None, ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        # request.remote_addr -> denemeyi yapan makinenin IP'si
        ip = request.remote_addr

        success = USERS.get(username) == password
        log_attempt(ip, username, success)

        if success:
            msg, cls = "Giriş başarılı! ✔", "ok"
        else:
            msg, cls = "Kullanıcı adı veya parola hatalı.", "no"
    return render_template_string(PAGE, msg=msg, cls=cls)


@app.route("/")
def index():
    return '<meta http-equiv="refresh" content="0; url=/login">'


if __name__ == "__main__":
    # host="0.0.0.0" -> aynı ağdaki diğer bilgisayarlar da erişebilir
    print("Hedef login calisiyor:  http://localhost:5000/login")
    print("Loglar:", os.path.abspath(LOG_FILE))
    app.run(host="0.0.0.0", port=5000, debug=False)
