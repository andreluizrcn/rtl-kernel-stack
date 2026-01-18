# Rtl-kernel-stack

**A complete hardware-to-software system demonstrator**

## Technical Definition

This project is a unified repository demonstrating vertical system integration across hardware RTL design, Linux kernel development, and userspace application programming. It implements a coherent pipeline from digital logic (SystemVerilog) through kernel-space drivers to user-space interfaces (C/C++/Python).

## Core Architecture

```
RTL (Digital Hardware) → Kernel Module → Userspace API → Automation Layer
```

## Key Components

1. **RTL Layer** (SystemVerilog)
   - Synchronous FIFO with configurable depth/width
   - Protocol FSM (IDLE→REQ→WAIT→DONE)
  
2. **Kernel Layer** (Linux)
   - Character device driver with `file_operations`
   - Concurrent access control (mutex)
   - IOCTL interface for configuration
   - MMAP for low-latency data transfer
   - Nanosecond timing via `ktime_get_ns()`

3. **Userspace Layer**
   - C application for direct hardware interaction
   - C++ wrapper for object-oriented interface
   - Python scripts for automation and analysis



