import json, os, re, sys, time, urllib.error, urllib.request

REPO, RUN, ATT = os.environ["REPO"], os.environ["RUN_ID"], os.environ["RUN_ATTEMPT"]
TOKEN = os.environ["GH_TOKEN"]
LINE = re.compile(r"^\S+ shipmate-state-digest=(none|([0-9a-f]{64}) path=(\S+))$")
T0 = time.time()


def stamp():
    return f"t+{time.time() - T0:6.2f}s"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


opener = urllib.request.build_opener(NoRedirect)


def get(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    try:
        with opener.open(req) as r:
            return r.status, r.read(), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers


def jobs(path):
    status, body, _ = get(path)
    if status != 200:
        print(stamp(), "listing", path, "->", status, body[:200])
        return []
    return json.loads(body)["jobs"]


def show(label, js):
    print(stamp(), label, len(js), "jobs")
    for j in js:
        print("   ", json.dumps({k: j.get(k) for k in (
            "id", "name", "run_attempt", "status", "conclusion", "started_at", "completed_at")}))


print(stamp(), f"reader start run={RUN} attempt={ATT}", time.strftime("%H:%M:%S", time.gmtime(T0)))
for i in range(60):
    latest = jobs(f"repos/{REPO}/actions/runs/{RUN}/jobs?filter=latest&per_page=100")
    cells = [j for j in latest if j["name"].startswith("cell")]
    show(f"poll {i} filter=latest", latest)
    if len(cells) == 3 and all(j["status"] == "completed" for j in cells):
        break
    time.sleep(2)
show("filter=all", jobs(f"repos/{REPO}/actions/runs/{RUN}/jobs?filter=all&per_page=100"))
show(f"attempts/{ATT}", jobs(f"repos/{REPO}/actions/runs/{RUN}/attempts/{ATT}/jobs?per_page=100"))

saved, none = [], []
for j in cells:
    log = None
    for k in range(30):
        status, body, headers = get(f"repos/{REPO}/actions/jobs/{j['id']}/logs")
        if status == 302:
            with urllib.request.urlopen(headers["Location"]) as r:
                log = r.read().decode("utf-8", "replace")
            print(stamp(), j["name"], f"log try {k}: 302 then {len(log)} bytes")
            break
        print(stamp(), j["name"], f"log try {k}: {status} {body[:120]!r}")
        time.sleep(2)
    if log is None:
        print(stamp(), j["name"], "log never readable")
        continue
    lines = log.splitlines()
    print(f"--- raw lines containing 'shipmate-' in {j['name']} (attempt {j['run_attempt']}):")
    for ln in lines:
        if "shipmate-" in ln:
            print("   ", repr(ln))
    hits = [m for m in map(LINE.match, lines) if m]
    print(stamp(), j["name"], "whole-line digest matches:", len(hits))
    if len(hits) != 1:
        continue
    cell = j["name"][len("cell ("):-1]
    if hits[0].group(1) == "none":
        none.append(cell)
    else:
        saved.append({"cell": cell, "digest": hits[0].group(2), "path": hits[0].group(3),
                      "attempt": j["run_attempt"]})

print(stamp(), "cells", json.dumps(saved), "none", json.dumps(none))
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"cells={json.dumps(saved)}\nnone={json.dumps(none)}\n")
