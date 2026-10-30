"""
بيجهز الدنيا:
  1) قاعدة بيانات SQLite فيها أرقام سبام (بتمثل الداتا بيز "التقيلة")
  2) Bloom Filter في Redis بيتحمل بنفس الأرقام

تشغيل:  python 01_seed.py --count 1000000
"""
import argparse
import random
import time

from common import BLOOM_KEY, get_db, get_redis, random_number


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1_000_000, help="عدد أرقام السبام")
    ap.add_argument("--error-rate", type=float, default=0.01, help="نسبة الـ false positive")
    args = ap.parse_args()

    rng = random.Random(7)
    t0 = time.time()
    numbers = set()
    while len(numbers) < args.count:
        numbers.add(random_number(rng))
    print(f"✔ اتولد {len(numbers):,} رقم ({time.time() - t0:.1f}s)")

    # --- SQLite ---
    db = get_db()
    db.execute("DROP TABLE IF EXISTS spam_numbers")
    db.execute("CREATE TABLE spam_numbers (number TEXT PRIMARY KEY)")
    db.executemany("INSERT INTO spam_numbers VALUES (?)", ((n,) for n in numbers))
    db.commit()
    print("✔ SQLite جاهزة")

    # --- Redis Bloom Filter ---
    r = get_redis()
    r.delete(BLOOM_KEY)
    # سعة أكبر شوية من العدد الفعلي علشان نسيب مساحة للنمو
    r.bf().reserve(BLOOM_KEY, args.error_rate, int(args.count * 1.2))

    batch, loaded = [], 0
    for n in numbers:
        batch.append(n)
        if len(batch) == 10_000:
            r.bf().madd(BLOOM_KEY, *batch)
            loaded += len(batch)
            batch.clear()
    if batch:
        r.bf().madd(BLOOM_KEY, *batch)
        loaded += len(batch)

    info = r.bf().info(BLOOM_KEY)
    print(f"✔ Bloom Filter اتحمل بـ {loaded:,} رقم")
    print(f"  Redis memory للـ key ده: {r.memory_usage(BLOOM_KEY) / 1024 / 1024:.2f} MB")
    print(f"  تفاصيل: {info}")


if __name__ == "__main__":
    main()
