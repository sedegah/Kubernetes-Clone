from __future__ import annotations

import argparse
import time
import sys


def run_worker(uid: str, image: str) -> None:
    # Very small simulated workload. This keeps the process alive and
    # periodically prints a heartbeat so supervisors can observe liveness.
    print(f"worker starting for pod {uid} image={image}")
    sys.stdout.flush()
    try:
        while True:
            print(f"heartbeat {uid}")
            sys.stdout.flush()
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"worker {uid} shutting down")
        sys.stdout.flush()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--uid", required=True)
    p.add_argument("--image", required=True)
    args = p.parse_args()
    run_worker(args.uid, args.image)


if __name__ == "__main__":
    main()
