"""app.py'yi değiştirmeden 5001 portunda çalıştırır (5000 macOS AirPlay tarafından dolu)."""
import os
from app import app, LOG_FILE

if __name__ == "__main__":
    print("Hedef login calisiyor:  http://localhost:5001/login")
    print("Loglar:", os.path.abspath(LOG_FILE))
    app.run(host="0.0.0.0", port=5001, debug=False)
