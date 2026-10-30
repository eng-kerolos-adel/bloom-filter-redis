"""
مدقق أرقام السبام (نفس فكرة Truecaller بشكل مبسط).

  - Bloom بيقول "لأ"  -> الرقم أكيد سليم، وقف فوراً (من غير ما نلمس الداتا بيز)
  - Bloom بيقول "آه"  -> غالباً سبام، نتأكد من الداتا بيز (علشان نلغي أي false positive)

تشغيل:  python 02_check.py 01012345678 01199999999
"""
import sys

from common import BLOOM_KEY, get_db, get_redis

r = get_redis()
db = get_db()


def is_spam(number: str) -> dict:
    if not r.bf().exists(BLOOM_KEY, number):
        return {"number": number, "spam": False, "db_hit": False, "via": "bloom (أكيد مش موجود)"}

    row = db.execute("SELECT 1 FROM spam_numbers WHERE number = ?", (number,)).fetchone()
    if row:
        return {"number": number, "spam": True, "db_hit": True, "via": "bloom + db (اتأكدنا)"}
    return {"number": number, "spam": False, "db_hit": True, "via": "false positive اتكشف من الداتا بيز"}


if __name__ == "__main__":
    for num in sys.argv[1:] or ["01012345678"]:
        print(is_spam(num))
