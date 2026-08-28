# Brute-Force Kalkanı

2 kişilik siber güvenlik projesi — bir login sistemine brute-force saldırısı yapan araç
ve karşısında bu saldırıyı tespit eden savunma servisi.

> ⚠️ Saldırı aracını **yalnızca bu repodaki kendi login sisteminize** karşı çalıştırın.
> Başkasına ait sistemlere brute-force yapmak yasa dışıdır.

## Klasör yapısı

```
brute-force-kalkani/
├── target/          → KİŞİ B (savunma): login sistemi + loglar
│   ├── app.py
│   └── requirements.txt
├── attacker/        → KİŞİ A (saldırı): brute-force script
│   ├── attack.py
│   ├── wordlist.txt
│   └── requirements.txt
└── README.md
```

## Hafta 1 — bugün kuracaklarınız

Bu iskelet uçtan uca çalışır: login denemeleri loglanır, saldırı script'i parolayı bulur.
Savunma servisi (logu okuyup alarm veren kısım) **Hafta 2**'de eklenecek.

### 1) Kişi B — login sistemini ayağa kaldır

```bash
cd target
pip install -r requirements.txt
python app.py
```

Tarayıcıdan aç: <http://localhost:5000/login>
Her deneme hem terminale basılır hem de `target/logs/login.log` dosyasına yazılır.

**Kendi IP'ni öğren** (Kişi A'ya vermen için):
- Windows: `ipconfig`  → "IPv4 Address"
- Mac/Linux: `ifconfig` ya da `ip a`  → örn. `192.168.1.34`

### 2) Kişi A — saldırıyı çalıştır

`attacker/attack.py` içindeki `TARGET_URL`'i ayarla:
- Aynı bilgisayardaysan: `http://localhost:5000/login`
- Kişi B'nin makinesindeyse: `http://192.168.1.34:5000/login` (onun IP'si)

```bash
cd attacker
pip install -r requirements.txt
python attack.py
```

Doğru parola (`secret123`) listede olduğu için saldırı onu bulup duracak.

### 3) Birlikte kontrol

`target/logs/login.log` dosyasını açın — saldırının bıraktığı onlarca `FAIL` satırını
ve en sonda bir `SUCCESS` satırını göreceksiniz. **İşte savunmanın Hafta 2'de okuyacağı veri bu.**

## Sonraki adımlar (özet)

- **Hafta 2:** Kişi A → hız/threading. Kişi B → logu okuyup "X sn'de N hata = şüpheli" tespiti.
- **Hafta 3:** Otomatik IP engelleme + alarm + izleme paneli.
- **Hafta 4:** Test, ince ayar, demo ve sunum.
