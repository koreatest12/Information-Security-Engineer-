import json
# 실제 shadow 필드: user:pass:last:min:max:warn:inact:exp:res
sample = "admin:$6$round=5000:19245:0:90:7:::"
fields = sample.split(':')
res = {"status": "✅ Secure (SHA-512)" if "$6$" in fields[1] else "⚠️ Weak"}
with open('data/shadow_report.json', 'w') as f:
    json.dump(res, f)
