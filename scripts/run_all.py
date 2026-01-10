#!/usr/bin/env python3

import subprocess
import sys

modules = ["fifo", "fsm", "uart"]

def run(module):
    print("=" * 40)
    print(f"[INFO] Running module: {module}")
    print("=" * 40)

    result = subprocess.run(
        ["./scripts/run_rtl.sh", module],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    if result.returncode != 0:
        print(f"[ERROR] Simulation failed for {module}")
        sys.exit(1)

if __name__ == "__main__":
    for m in modules:
        run(m)

    print("\n[OK] All RTL simulations completed successfully")

