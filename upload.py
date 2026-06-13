import json, base64, urllib.request, os, sys

TOKEN = sys.argv[1]
OWNER = "snowfrost"
REPO = "bobee-publisher"
BASE = "https://api.github.com"

files = {}
for root, dirs, filenames in os.walk("."):
    if ".git" in root:
        continue
    for f in filenames:
        path = os.path.join(root, f).replace("\\", "/").lstrip("./")
        with open(path, "rb") as fh:
            files[path] = fh.read()

print(f"Files to upload: {len(files)}")
for p in sorted(files.keys()):
    size = len(files[p])
    content = base64.b64encode(files[p]).decode()
    url = f"{BASE}/repos/{OWNER}/{REPO}/contents/{p}"
    payload = json.dumps({"message": f"Add {p}", "content": content}).encode()
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        sha = result.get("content", {}).get("sha", "?")
        print(f"  OK: {p} ({size} bytes)")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  FAIL: {p} ({size} bytes) HTTP {e.code}: {body[:200]}")
    except Exception as e:
        print(f"  FAIL: {p} - {e}")

print("\nDone!")
