"""
Benchmark أمين: بنقيس "كام مرة روحنا للداتا بيز" مع Bloom Filter وبدونه.

ملحوظة مهمة: SQLite شغالة جوه نفس العملية فهي سريعة جداً بشكل غير واقعي.
في الإنتاج الداتا بيز بتبقى على الشبكة وكل Query بياخد 1-5ms على الأقل.
علشان كده فيه --db-latency-ms بيحاكي زمن رحلة الشبكة للداتا بيز.

تشغيل:  python 03_benchmark.py --queries 5000 --spam-ratio 0.01 --db-latency-ms 2
"""
import argparse
import random
import time

from common import BLOOM_KEY, get_db, get_redis, random_number


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", type=int, default=5000)
    ap.add_argument("--spam-ratio", type=float, default=0.01, help="نسبة الأرقام السبام فعلاً في الطلبات")
    ap.add_argument("--db-latency-ms", type=float, default=2.0, help="زمن رحلة الشبكة للداتا بيز (محاكاة)")
    args = ap.parse_args()

    r, db = get_redis(), get_db()
    rng = random.Random(123)

    spam_pool = [row[0] for row in db.execute(
        "SELECT number FROM spam_numbers ORDER BY RANDOM() LIMIT ?", (args.queries,))]
    queries = [
        rng.choice(spam_pool) if rng.random() < args.spam_ratio else random_number(rng)
        for _ in range(args.queries)
    ]
    latency = args.db_latency_ms / 1000

    def db_lookup(num):
        time.sleep(latency)  # محاكاة الشبكة
        return db.execute("SELECT 1 FROM spam_numbers WHERE number = ?", (num,)).fetchone() is not None

    # --- 1) من غير Bloom: كل طلب يروح الداتا بيز ---
    t0 = time.perf_counter()
    truth = [db_lookup(q) for q in queries]
    naive_time = time.perf_counter() - t0
    naive_db_calls = len(queries)

    # --- 2) مع Bloom ---
    db_calls = false_pos = 0
    t0 = time.perf_counter()
    for q in queries:
        if r.bf().exists(BLOOM_KEY, q):
            db_calls += 1
            if not db_lookup(q):
                false_pos += 1
    bloom_time = time.perf_counter() - t0

    saved = 1 - db_calls / naive_db_calls
    print("=" * 56)
    print(f"عدد الطلبات: {args.queries:,} | نسبة السبام الحقيقية: {args.spam_ratio:.1%}")
    print(f"زمن الداتا بيز المحاكي: {args.db_latency_ms} ms")
    print("-" * 56)
    print(f"بدون Bloom : DB calls = {naive_db_calls:>6,} | الوقت = {naive_time:6.2f}s")
    print(f"مع Bloom   : DB calls = {db_calls:>6,} | الوقت = {bloom_time:6.2f}s")
    print(f"False positives اتكشفت: {false_pos}")
    print("-" * 56)
    print(f"✅ وفرنا {saved:.1%} من ضغط الداتا بيز | تسريع {naive_time / bloom_time:.1f}x")
    print("=" * 56)
    print("افتكر: التوفير بيعتمد على نسبة الطلبات اللي نتيجتها 'مش موجود'.")


if __name__ == "__main__":
    main()
