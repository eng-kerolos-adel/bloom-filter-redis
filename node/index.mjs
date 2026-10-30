// مثال Node.js: Bloom Filter على Redis باستخدام الأوامر المباشرة (sendCommand)
// تشغيل:  npm install && npm start
import { createClient } from "redis";

const client = createClient({ url: process.env.REDIS_URL ?? "redis://localhost:6379" });
client.on("error", (e) => console.error("Redis error:", e));
await client.connect();

const KEY = "demo:emails";
await client.del(KEY);

// BF.RESERVE key error_rate capacity
await client.sendCommand(["BF.RESERVE", KEY, "0.01", "100000"]);

// BF.ADD -> 1 لو اتضاف جديد، 0 لو غالباً كان موجود
console.log("ADD  kero@example.com  ->", await client.sendCommand(["BF.ADD", KEY, "kero@example.com"]));
console.log("ADD  kero@example.com  ->", await client.sendCommand(["BF.ADD", KEY, "kero@example.com"]));

// BF.EXISTS -> 1 = غالباً موجود | 0 = أكيد مش موجود
console.log("EXISTS kero@example.com ->", await client.sendCommand(["BF.EXISTS", KEY, "kero@example.com"]));
console.log("EXISTS nobody@example.com ->", await client.sendCommand(["BF.EXISTS", KEY, "nobody@example.com"]));

// Batch: BF.MADD / BF.MEXISTS
await client.sendCommand(["BF.MADD", KEY, "a@x.com", "b@x.com", "c@x.com"]);
console.log("MEXISTS ->", await client.sendCommand(["BF.MEXISTS", KEY, "a@x.com", "zzz@x.com"]));

console.log("INFO ->", await client.sendCommand(["BF.INFO", KEY]));
await client.quit();
