"""attack.py'yi değiştirmeden 5001 portundaki hedefe yöneltip çalıştırır."""
import attack

attack.TARGET_URL = "http://localhost:5001/login"
attack.main()
