#!/usr/bin/env python3
# run_all.py - Main automation script for rtl-kernel-stack

import subprocess
import sys
import os
from datetime import datetime

class RTLKernelStack:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.results_dir = os.path.join(self.root_dir, "results")
        self.log_dir = os.path.join(self.results_dir, "logs")
        
        # Ensure directories exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Module configuration
        self.rtl_modules = ["fifo", "fsm", "uart"]
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
        # Save to log file
        with open(os.path.join(self.log_dir, "run_all.log"), "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def run_rtl_simulation(self, module):
        """Run RTL simulation for a specific module"""
        self.log(f"Starting RTL simulation: {module}")
        
        script_path = os.path.join(self.root_dir, "scripts", "run_rtl.sh")
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
        result = subprocess.run(
            [script_path],
            cwd=self.root_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log(f"Driver test failed", "ERROR")
            self.log(f"Stderr: {result.stderr}", "ERROR")
            return False
        
        self.log("Driver test completed")
        return True
    
    def run_userspace_tests(self):
        """Run userspace tests"""
        self.log("Starting userspace tests")
        
        tests = [
            ("userspace/c", "ll_raw_test.c", "ll_test"),
            ("userspace/cpp", "ll_bench.cpp", "ll_bench")
        ]
        
        for path, source, binary in tests:
            src_path = os.path.join(self.root_dir, path, source)
            bin_path = os.path.join(self.root_dir, path, binary)
            
            # Compile
            self.log(f"Compiling {source}")
            compile_cmd = ["gcc" if source.endswith(".c") else "g++", 
                          "-o", bin_path, src_path, "-lrt", "-pthread", "-O2"]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"Failed to compile {source}", "WARN")
                continue
            
            # Execute
            self.log(f"Running {binary}")
            run_result = subprocess.run([bin_path], capture_output=True, text=True)
            if run_result.returncode == 0:
                self.log(f"Result {binary}:\n{run_result.stdout}")
            else:
                self.log(f"Failed to run {binary}", "WARN")
        
        self.log("Userspace tests completed")
        return True
    
    def run_analysis(self):
        """Run results analysis"""
        self.log("Starting results analysis")
        
        python_script = os.path.join(self.root_dir, "userspace", "python", "analyze.py")
        if os.path.exists(python_script):
            result = subprocess.run([sys.executable, python_script], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Analysis completed:\n{result.stdout}")
            else:
                self.log(f"Analysis failed: {result.stderr}", "WARN")
        
        return True
    
    def run_all(self):
        """Run the entire pipeline"""
        self.log("=" * 60)
        self.log("STARTING RTL-KERNEL-STACK - COMPLETE EXECUTION")
        self.log("=" * 60)
        
        # Phase 1: RTL Simulations
        self.log("\n" + "=" * 60)
        self.log("PHASE 1: RTL SIMULATION")
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
        
        # Phase 3: Userspace Tests
        self.log("\n" + "=" * 60)
        self.log("PHASE 3: USERSPACE")
        self.log("=" * 60)
        
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
    print("═" * 70)
    
    # Check dependencies
    print("\n[INFO] Checking dependencies...")
    
    dependencies = ["iverilog", "vvp", "gcc", "g++", "python3"]
    missing = []
    
    for dep in dependencies:
        result = subprocess.run(["which", dep], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"[WARN] Missing dependencies: {', '.join(missing)}")
        print("[INFO] Some functionalities may not be available")
    
    # Execute pipeline
    project = RTLKernelStack()
    
    try:
        success = project.run_all()
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
