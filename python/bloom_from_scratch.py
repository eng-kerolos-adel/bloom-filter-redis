"""
Bloom Filter من الصفر بدون أي مكتبات (بايثون صافي).
الهدف: تفهم اللي بيحصل جوه Redis بالظبط.

تشغيل:  python bloom_from_scratch.py
"""
import hashlib
import math
import random


class BloomFilter:
    def __init__(self, capacity: int, error_rate: float = 0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        # m = عدد البتات   |   k = عدد دوال الهاش
        self.m = math.ceil(-capacity * math.log(error_rate) / (math.log(2) ** 2))
        self.k = max(1, round((self.m / capacity) * math.log(2)))
        self.bits = bytearray((self.m + 7) // 8)

    def _positions(self, item):
        # Double hashing: من هاش واحد بنطلع k مواضع مختلفة
        digest = hashlib.sha256(str(item).encode()).digest()
        h1 = int.from_bytes(digest[:8], "big")
        h2 = int.from_bytes(digest[8:16], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item) -> None:
        for pos in self._positions(item):
            self.bits[pos >> 3] |= 1 << (pos & 7)

    def __contains__(self, item) -> bool:
        return all(self.bits[pos >> 3] & (1 << (pos & 7)) for pos in self._positions(item))

    @property
    def size_kb(self) -> float:
        return len(self.bits) / 1024


if __name__ == "__main__":
    N = 100_000
    bf = BloomFilter(capacity=N, error_rate=0.01)
    print(f"عدد البتات m = {bf.m:,} | دوال الهاش k = {bf.k} | الحجم = {bf.size_kb:,.0f} KB")

    members = [f"member-{i}" for i in range(N)]
    for x in members:
        bf.add(x)

    # 1) مفيش false negative أبداً
    assert all(x in bf for x in members), "حصلت مصيبة: false negative!"
    print("✅ كل العناصر اللي اتضافت اتلقت (صفر false negatives)")

    # 2) نقيس نسبة الـ false positives على عناصر عمرها ما اتضافت
    rng = random.Random(42)
    tests = [f"stranger-{rng.randrange(10**12)}" for _ in range(N)]
    fp = sum(1 for x in tests if x in bf)
    print(f"⚠️  false positives: {fp:,} من {N:,}  =  {fp / N:.2%}  (المستهدف {bf.error_rate:.0%})")
