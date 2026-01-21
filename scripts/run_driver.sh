#!/bin/bash
# scripts/run_driver.sh
set -e

ROOT_DIR=$(pwd)
KERNEL_DIR="$ROOT_DIR/kernel/ll_driver"
RESULTS_DIR="$ROOT_DIR/results"
LOG_DIR="$RESULTS_DIR/logs"

mkdir -p "$LOG_DIR"

echo "[INFO] Building kernel module..."
cd "$KERNEL_DIR"
make clean
make
echo "[OK] Module built successfully"

echo "[INFO] Installing module..."
sudo rmmod ll_driver 2>/dev/null || true
sudo insmod ll_driver.ko
sudo chmod 666 /dev/ll_driver 2>/dev/null || true

echo "[INFO] Testing module..."
if [ -c /dev/ll_driver ]; then
    echo "[OK] Device created at /dev/ll_driver"
else
    echo "[ERROR] Device not created!"
    exit 1
fi

# Run userspace test
echo "[INFO] Running userspace test..."
cd "$ROOT_DIR/userspace/c"
gcc -o ll_test ll_raw_test.c -lrt
sudo ./ll_test 2>&1 | tee "$LOG_DIR/driver_test.log"

echo "[INFO] Driver test completed"
dmesg | grep "LL_DRIVER" | tail -10
