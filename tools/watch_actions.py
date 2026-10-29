"""Wait for the push workflow on an exact commit; check every three minutes."""
import argparse
from datetime import datetime, timezone
import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


def watch(repository, sha, interval=180, timeout=3600):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        url = f"https://api.github.com/repos/{repository}/actions/runs?head_sha={sha}&event=push&per_page=10"
        try:
            request = Request(url, headers={"Accept": "application/vnd.github+json",
                                           "User-Agent": "tofu65-build-monitor"})
            with urlopen(request, timeout=30) as response:
                runs = json.load(response)["workflow_runs"]
            runs = [run for run in runs if run["path"] == ".github/workflows/build.yml"]
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if runs:
                run = max(runs, key=lambda item: item["id"])
                print(f"{now} {run['status']} {run['conclusion']} {run['html_url']}", flush=True)
                if run["status"] == "completed":
                    return 0 if run["conclusion"] == "success" else 1
            else:
                print(f"{now} Waiting for workflow registration: {sha}", flush=True)
        except (URLError, TimeoutError) as error:
            print(f"Temporary API error: {error}; retrying", flush=True)
        # Short sleeps permit prompt interruption without changing API cadence.
        next_poll = min(time.monotonic() + interval, deadline)
        while time.monotonic() < next_poll:
            time.sleep(min(30, next_poll - time.monotonic()))
    print("Monitoring timed out; build success has NOT been confirmed.", flush=True)
    return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="thsrhwk01/zmk-kbdfans_tofu65-3.0")
    parser.add_argument("--sha", required=True)
    parser.add_argument("--interval", type=int, default=180)
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    if args.interval < 30 or args.timeout < 1:
        parser.error("interval must be at least 30 seconds and timeout positive")
    raise SystemExit(watch(args.repository, args.sha, args.interval, args.timeout))
