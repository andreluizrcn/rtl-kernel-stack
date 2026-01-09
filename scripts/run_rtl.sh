#!/bin/bash
set -e

ROOT_DIR=$(pwd)
RESULTS_DIR="$ROOT_DIR/results/logs"
RTL_DIR="$ROOT_DIR/rtl"

mkdir -p "$RESULTS_DIR"

MODULE=$1

if [ -z "$MODULE" ]; then
  echo "Usage: ./run_rtl.sh {fifo|fsm|uart}"
  exit 1
fi

case $MODULE in
  fifo)
    SRC="$RTL_DIR/fifo/fifo.sv"
    TB="$RTL_DIR/fifo/fifo_tb.sv"
    ;;
  fsm)
    SRC="$RTL_DIR/fsm/protocol_fsm.sv"
    TB="$RTL_DIR/fsm/protocol_fsm_tb.sv"
    ;;
  uart)
    SRC="$RTL_DIR/uart_tx/uart_tx.sv"
    TB="$RTL_DIR/uart_tx/uart_tx_tb.sv"
    ;;
  *)
    echo "Invalid module: $MODULE"
    exit 1
    ;;
esac

OUT="sim_$MODULE.out"
LOG="$RESULTS_DIR/${MODULE}_sim.log"

echo "[INFO] Compiling $MODULE..."
iverilog -g2012 "$SRC" "$TB" -o "$OUT"

echo "[INFO] Running simulation..."
vvp "$OUT" | tee "$LOG"

echo "[OK] $MODULE simulation completed successfully"

