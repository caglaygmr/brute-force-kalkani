import os
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict
LOG_FILE = os.path.join("logs", "login.log")
# Ayarlar (Kurallar)
WINDOW_SECONDS = 10   # Kontrol edilecek zaman aralığı (saniye)
THRESHOLD = 5         # Bu süre içinde izin verilen max hatalı deneme
# Her IP için son hatalı girişlerin zaman damgalarını tutan sözlük
# Örn: {"192.168.1.34": [datetime1, datetime2, ...]}
failed_attempts = defaultdict(list)
def parse_log_line(line):
    """
    Log satırını ayrıştırır.
    Örnek format: 2026-08-28 10:30:15  IP=127.0.0.1  user=admin  result=FAIL
    """
    pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+IP=([\d\.]+)\s+user=(\w+)\s+result=(\w+)"
    match = re.search(pattern, line)
    if match:
        dt_str, ip, user, result = match.groups()
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt, ip, user, result
    return None
def check_for_attack(ip, attempt_time):
    """Gelen hatalı denemenin bir saldırı olup olmadığını kontrol eder."""
    # Yeni denemeyi ekle
    failed_attempts[ip].append(attempt_time)
    
    # 10 saniyeden eski kayıtları temizle (Sliding Window)
    cutoff_time = attempt_time - timedelta(seconds=WINDOW_SECONDS)
    failed_attempts[ip] = [t for t in failed_attempts[ip] if t > cutoff_time]
    
    # Eşik kontrolü
    count = len(failed_attempts[ip])
    if count >= THRESHOLD:
        print(f"\n🚨 [ALARM] Brute-Force Saldırısı Tespit Edildi!")
        print(f"   └── Hedef IP: {ip}")
        print(f"   └── Detay   : Son {WINDOW_SECONDS} saniyede {count} hatalı deneme!\n")
def watch_logs():
    """login.log dosyasını canlı takip eder."""
    print("🛡️ [SAVUNMA MOTORU] Başlatıldı. Loglar canlı dinleniyor...")
    
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a").close()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        # Dosyanın en sonuna git (önceki eski kayıtları atla)
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)  # Yeni satır yoksa bekle
                continue
            
            parsed = parse_log_line(line.strip())
            if parsed:
                dt, ip, user, result = parsed
                if result == "FAIL":
                    check_for_attack(ip, dt)
                elif result == "SUCCESS":
                    # Başarılı girişte o IP'nin hatalarını sıfırlayabilirsin
                    failed_attempts[ip].clear()
if __name__ == "__main__":
    watch_logs()