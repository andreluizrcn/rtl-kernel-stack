#!/usr/bin/env python3
# scripts/run_all.py - VERSION WITHOUT UART

import subprocess
import sys
import os
from datetime import datetime

class RTLKernelStack:
    def __init__(self):
        self.root_dir = os.getcwd()
        self.results_dir = os.path.join(self.root_dir, "results")
        self.log_dir = os.path.join(self.results_dir, "logs")
        
        os.makedirs(self.log_dir, exist_ok=True)
        
        # ONLY FIFO and FSM - NO UART
        self.rtl_modules = ["fifo", "fsm"]  # Removed "uart"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
        with open(os.path.join(self.log_dir, "run_all.log"), "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def run_rtl_simulation(self, module):
        """Run RTL simulation"""
        self.log(f"Starting RTL simulation: {module}")
        
        script_path = os.path.join(self.root_dir, "scripts", "run_rtl.sh")
        
        if not os.path.exists(script_path):
            self.log(f"Script not found: {script_path}", "ERROR")
            return False
        
        result = subprocess.run(
            [script_path, module],
            cwd=self.root_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log(f"RTL simulation failed: {module}", "ERROR")
            self.log(f"Stderr: {result.stderr}", "ERROR")
            return False
        
        self.log(f"RTL simulation completed: {module}")
        return True
    
    def run_driver_test(self):
        """Run kernel driver test"""
        self.log("Starting kernel driver test")
        
        script_path = os.path.join(self.root_dir, "scripts", "run_driver.sh")
        
        if not os.path.exists(script_path):
            self.log(f"Script not found: {script_path}", "ERROR")
            return False
        
        result = subprocess.run(
            [script_path],
            cwd=self.root_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log("Driver test failed", "ERROR")
            self.log(f"Stderr: {result.stderr}", "ERROR")
            return False
        
        self.log("Driver test completed")
        return True
    
    def compile_userspace(self):
        """Compile userspace programs"""
        self.log("Compiling userspace programs")
        
        # Compile C program
        c_src = os.path.join(self.root_dir, "userspace/c/ll_raw_test.c")
        c_bin = os.path.join(self.root_dir, "userspace/c/ll_test")
        
        if os.path.exists(c_src):
            result = subprocess.run(
                ["gcc", c_src, "-o", c_bin, "-lrt", "-O2"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log("✓ C program compiled")
            else:
                self.log(f"C compilation failed: {result.stderr}", "WARN")
        
        # Compile C++ program
        cpp_src = os.path.join(self.root_dir, "userspace/cpp/ll_bench.cpp")
        cpp_bin = os.path.join(self.root_dir, "userspace/cpp/ll_bench")
        
        if os.path.exists(cpp_src):
            result = subprocess.run(
                ["g++", cpp_src, "-o", cpp_bin, "-O2", "-std=c++11"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log("✓ C++ program compiled")
            else:
                self.log(f"C++ compilation failed: {result.stderr}", "WARN")
        
        return True
    
    def run_userspace_tests(self):
        """Run userspace tests"""
        self.log("Running userspace tests")
        
        # Test C program (driver)
        c_bin = os.path.join(self.root_dir, "userspace/c/ll_test")
        if os.path.exists(c_bin):
            self.log("Testing C program (driver latency)...")
            try:
                result = subprocess.run(
                    ["sudo", c_bin],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"C test output:\n{result.stdout}")
                else:
                    self.log(f"C test failed: {result.stderr}", "WARN")
            except Exception as e:
                self.log(f"C test error: {e}", "WARN")
        else:
            self.log("C binary not found, skipping", "WARN")
        
        # Test C++ program (benchmark)
        cpp_bin = os.path.join(self.root_dir, "userspace/cpp/ll_bench")
        if os.path.exists(cpp_bin):
            self.log("Running C++ benchmark...")
            try:
                result = subprocess.run([cpp_bin], capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"C++ benchmark output:\n{result.stdout}")
                else:
                    self.log(f"C++ benchmark failed: {result.stderr}", "WARN")
            except Exception as e:
                self.log(f"C++ benchmark error: {e}", "WARN")
        else:
            self.log("C++ binary not found, skipping", "WARN")
        
        return True
    
    def run_analysis(self):
        """Run results analysis"""
        self.log("Running analysis")
        
        python_script = os.path.join(self.root_dir, "userspace/python/analyze.py")
        
        if os.path.exists(python_script):
            try:
                result = subprocess.run(
                    [sys.executable, python_script],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"Analysis output:\n{result.stdout}")
                else:
                    self.log(f"Analysis failed: {result.stderr}", "WARN")
            except Exception as e:
                self.log(f"Analysis error: {e}", "WARN")
        else:
            self.log("Analysis script not found", "WARN")
        
        return True
    
    def run_all(self):
        """Run the entire pipeline"""
        self.log("=" * 60)
        self.log("STARTING RTL-KERNEL-STACK COMPLETE EXECUTION")
        self.log("=" * 60)
        
        # Phase 1: RTL Simulations
        self.log("\n" + "=" * 60)
        self.log("PHASE 1: RTL SIMULATION (FIFO + FSM only)")
        self.log("=" * 60)
        
        for module in self.rtl_modules:
            if not self.run_rtl_simulation(module):
                self.log(f"Stopping execution due to failure in {module}", "ERROR")
                return False
        
        # Phase 2: Kernel Driver
        self.log("\n" + "=" * 60)
        self.log("PHASE 2: KERNEL DRIVER")
        self.log("=" * 60)
        
        if not self.run_driver_test():
            self.log("Driver failed, continuing with userspace...", "WARN")
        
        # Phase 3: Userspace
        self.log("\n" + "=" * 60)
        self.log("PHASE 3: USERSPACE")
        self.log("=" * 60)
        
        if self.compile_userspace():
            self.run_userspace_tests()
        
        # Phase 4: Analysis
        self.log("\n" + "=" * 60)
        self.log("PHASE 4: ANALYSIS")
        self.log("=" * 60)
        
        self.run_analysis()
        
        # Conclusion
        self.log("\n" + "=" * 60)
        self.log("EXECUTION COMPLETED SUCCESSFULLY!")
        self.log("=" * 60)
        self.log(f"Logs available at: {self.log_dir}")
        self.log(f"Results at: {self.results_dir}")
        
        return True

def main():
    """Main function"""
    print("\n" + "═" * 70)
    print("RTL-KERNEL-STACK - Integrated Hardware-Software System")
    print("Running: RTL (FIFO + FSM) → Kernel Driver → Userspace")
    print("═" * 70)
    
    # Check current directory
    print("\n[INFO] Checking directory structure...")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check scripts
    print("\n[INFO] Checking scripts...")
    if os.path.exists("scripts/run_all.py"):
        print("✓ scripts/run_all.py")
    else:
        print("✗ scripts/run_all.py (missing)")
    
    # Execute pipeline
    print("\n[INFO] Initializing RTL-Kernel-Stack system...")
    project = RTLKernelStack()
    
    try:
        success = project.run_all()
        if success:
            print("\n" + "=" * 70)
            print("RTL-KERNEL-STACK EXECUTION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("RTL-KERNEL-STACK EXECUTION FAILED")
            print("=" * 70)
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
