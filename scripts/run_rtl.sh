#!/bin/bash
set -e

# Root directories
ROOT_DIR=$(pwd)
RTL_DIR="$ROOT_DIR/rtl"
RESULTS_DIR="$ROOT_DIR/results"
LOG_DIR="$RESULTS_DIR/logs"
PLOT_DIR="$RESULTS_DIR/plots"

# Create output directories if they do not exist
mkdir -p "$LOG_DIR" "$PLOT_DIR"

MODULE=$1

if [ -z "$MODULE" ]; then
  echo "Usage: ./run_rtl.sh {fifo|fsm|uart}"
  exit 1
fi

# Select RTL and testbench
case $MODULE in
  fifo)
    SRC="$RTL_DIR/fifo/sync_fifo.sv"
    TB="$RTL_DIR/fifo/fifo_tb.sv"
    VCD="fifo.vcd"
    ;;
  fsm)
    SRC="$RTL_DIR/fsm/protocol_fsm.sv"
    TB="$RTL_DIR/fsm/protocol_fsm_tb.sv"
    VCD="fsm.vcd"
    ;;
  uart)
    SRC="$RTL_DIR/uart_tx/uart_tx.sv"
    TB="$RTL_DIR/uart_tx/uart_tx_tb.sv"
    VCD="uart.vcd"
    ;;
  *)
    echo "Invalid module: $MODULE"
    exit 1
    ;;
esac

OUT="sim_${MODULE}.out"
LOG="$LOG_DIR/${MODULE}.log"

echo "[INFO] Running RTL simulation: $MODULE"

echo "[INFO] Compiling RTL + testbench..."
iverilog -g2012 "$SRC" "$TB" -o "$OUT"

echo "[INFO] Running simulation..."
vvp "$OUT" | tee "$LOG"

# Move waveform to results/plots
if [ -f "$VCD" ]; then
  mv "$VCD" "$PLOT_DIR/"
  echo "[INFO] Waveform saved to results/plots/$VCD"
else
  echo "[WARN] No VCD file generated"
fi

echo "[OK] Simulation for $MODULE completed successfully"

