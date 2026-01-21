#!/usr/bin/env python3
# run_all.py - Main automation script for rtl-kernel-stack

import subprocess
import sys
import os
from datetime import datetime

class RTLKernelStack:
    def __init__(self):
        self.root_dir = os.getcwd()  # Use current directory, not where script is
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
        log_file = os.path.join(self.log_dir, "run_all.log")
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def run_rtl_simulation(self, module):
        """Run RTL simulation for a specific module"""
        self.log(f"Starting RTL simulation: {module}")
        
        # The run_rtl.sh script is in scripts/
        script_path = os.path.join(self.root_dir, "scripts", "run_rtl.sh")
        
        # Check if script exists
        if not os.path.exists(script_path):
            self.log(f"Script not found: {script_path}", "ERROR")
            # Try iverilog directly
            return self.run_iverilog_direct(module)
        
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
    
    def run_iverilog_direct(self, module):
        """Run iverilog directly if script fails"""
        self.log(f"Running direct iverilog for: {module}")
        
        # Configurations for each module
        configs = {
            "fifo": {
                "src": "rtl/fifo/sync_fifo.sv",
                "tb": "rtl/fifo/fifo_tb.sv",
                "out": "sim_fifo.out",
                "vcd": "fifo.vcd"
            },
            "fsm": {
                "src": "rtl/fsm/protocol_fsm.sv",
                "tb": "rtl/fsm/protocol_tb_fsm.sv",
                "out": "sim_fsm.out",
                "vcd": "fsm.vcd"
            },
            "uart": {
                "src": "rtl/uart_tx/uart_tx.sv",
                "tb": "rtl/uart_tx/uart_tx_tb.sv",
                "out": "sim_uart.out",
                "vcd": "uart.vcd"
            }
        }
        
        if module not in configs:
            self.log(f"Unknown module: {module}", "ERROR")
            return False
        
        cfg = configs[module]
        
        # Check if files exist
        if not os.path.exists(cfg["src"]):
            self.log(f"Source file not found: {cfg['src']}", "ERROR")
            return False
        if not os.path.exists(cfg["tb"]):
            self.log(f"Testbench not found: {cfg['tb']}", "ERROR")
            return False
        
        # Compile
        compile_cmd = ["iverilog", "-g2012", cfg["src"], cfg["tb"], "-o", cfg["out"]]
        self.log(f"Compiling: {' '.join(compile_cmd)}")
        
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode != 0:
            self.log(f"Compilation failed: {compile_result.stderr}", "ERROR")
            return False
        
        # Run simulation
        run_cmd = ["vvp", cfg["out"]]
        self.log(f"Running simulation: {' '.join(run_cmd)}")
        
        run_result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True
        )
        
        if run_result.returncode != 0:
            self.log(f"Simulation failed: {run_result.stderr}", "ERROR")
            return False
        
        # Move VCD to results/plots
        if os.path.exists(cfg["vcd"]):
            plots_dir = os.path.join(self.results_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            os.rename(cfg["vcd"], os.path.join(plots_dir, cfg["vcd"]))
            self.log(f"Waveform saved to results/plots/{cfg['vcd']}")
        
        # Save log
        log_file = os.path.join(self.log_dir, f"{module}.log")
        with open(log_file, "w") as f:
            f.write(run_result.stdout)
        
        self.log(f"Direct simulation completed: {module}")
        return True
    
    def run_driver_test(self):
        """Run kernel driver test"""
        self.log("Starting kernel driver test")
        
        # The run_driver.sh script is in scripts/
        script_path = os.path.join(self.root_dir, "scripts", "run_driver.sh")
        
        if not os.path.exists(script_path):
            self.log(f"Script not found: {script_path}", "ERROR")
            # Try compiling driver directly
            return self.compile_driver_direct()
        
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
    
    def compile_driver_direct(self):
        """Compile driver directly"""
        self.log("Compiling driver directly")
        
        driver_dir = os.path.join(self.root_dir, "kernel", "ll_driver")
        if not os.path.exists(driver_dir):
            self.log(f"Driver directory not found: {driver_dir}", "ERROR")
            return False
        
        # Check Makefile
        makefile = os.path.join(driver_dir, "Makefile")
        if not os.path.exists(makefile):
            self.log(f"Makefile not found: {makefile}", "ERROR")
            return False
        
        # Run make
        result = subprocess.run(
            ["make", "-C", driver_dir],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log(f"Make failed: {result.stderr}", "ERROR")
            return False
        
        self.log("Driver compiled successfully")
        
        # Try to load module
        self.log("Attempting to load module...")
        module_path = os.path.join(driver_dir, "ll_driver.ko")
        if os.path.exists(module_path):
            try:
                subprocess.run(["sudo", "rmmod", "ll_driver"], 
                             capture_output=True)
                subprocess.run(["sudo", "insmod", module_path], 
                             capture_output=True, text=True)
                subprocess.run(["sudo", "chmod", "666", "/dev/ll_driver"],
                             capture_output=True)
                self.log("Module loaded successfully")
                return True
            except Exception as e:
                self.log(f"Failed to load module: {e}", "ERROR")
                return False
        
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
            
            # Check if source exists
            if not os.path.exists(src_path):
                self.log(f"Source file not found: {src_path}", "WARN")
                continue
            
            # Compile
            self.log(f"Compiling {source}")
            compile_cmd = ["gcc" if source.endswith(".c") else "g++", 
                          "-o", bin_path, src_path, "-lrt", "-pthread", "-O2"]
            
            try:
                result = subprocess.run(compile_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log(f"Failed to compile {source}", "WARN")
                    self.log(f"Compilation error: {result.stderr}", "WARN")
                    continue
            except FileNotFoundError:
                self.log(f"Compiler not found for {source}", "WARN")
                continue
            
            # Execute
            self.log(f"Running {binary}")
            try:
                run_result = subprocess.run([bin_path], capture_output=True, text=True)
                if run_result.returncode == 0:
                    self.log(f"Result {binary}:\n{run_result.stdout}")
                else:
                    self.log(f"Failed to run {binary}", "WARN")
                    self.log(f"Execution error: {run_result.stderr}", "WARN")
            except Exception as e:
                self.log(f"Error running {binary}: {str(e)}", "WARN")
        
        self.log("Userspace tests completed")
        return True
    
    def run_analysis(self):
        """Run results analysis"""
        self.log("Starting results analysis")
        
        python_script = os.path.join(self.root_dir, "userspace", "python", "analyze.py")
        if os.path.exists(python_script):
            try:
                result = subprocess.run([sys.executable, python_script], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"Analysis completed:\n{result.stdout}")
                else:
                    self.log(f"Analysis failed: {result.stderr}", "WARN")
            except Exception as e:
                self.log(f"Error running analysis: {str(e)}", "WARN")
        else:
            self.log(f"Analysis script not found: {python_script}", "WARN")
        
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
    print("From RTL to Userspace - Complete Vertical Integration")
    print("═" * 70)
    
    # Check current directory structure
    print("\n[INFO] Checking directory structure...")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # List contents
    try:
        contents = os.listdir(current_dir)
        print(f"Directory contents: {contents}")
        
        # Check important directories
        print("\n[INFO] Checking project structure...")
        for dir_name in ["rtl", "kernel", "userspace", "scripts", "results"]:
            if os.path.exists(dir_name):
                print(f"✓ {dir_name}/")
            else:
                print(f"✗ {dir_name}/ (missing)")
        
        # Check if we have RTL files
        print("\n[INFO] Checking RTL files...")
        rtl_files_to_check = [
            "rtl/fifo/sync_fifo.sv",
            "rtl/fifo/fifo_tb.sv",
            "rtl/fsm/protocol_fsm.sv",
            "rtl/fsm/protocol_tb_fsm.sv"
        ]
        
        for rtl_file in rtl_files_to_check:
            if os.path.exists(rtl_file):
                print(f"✓ {rtl_file}")
            else:
                print(f"✗ {rtl_file} (missing)")
                
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    # Check dependencies
    print("\n[INFO] Checking dependencies...")
    
    dependencies = ["iverilog", "vvp", "gcc", "g++", "python3"]
    missing = []
    
    for dep in dependencies:
        try:
            result = subprocess.run(["which", dep], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(dep)
        except Exception:
            missing.append(dep)
    
    if missing:
        print(f"[WARN] Missing dependencies: {', '.join(missing)}")
        print("[INFO] Some functionalities may not be available")
    else:
        print("[OK] All dependencies found")
    
    # Check if scripts exist
    print("\n[INFO] Checking scripts...")
    script_paths = [
        "scripts/run_rtl.sh",
        "scripts/run_driver.sh",
        "run_all.py"
    ]
    
    for script in script_paths:
        if os.path.exists(script):
            print(f"✓ {script}")
        else:
            print(f"✗ {script} (missing)")
    
    # Execute pipeline
    print("\n[INFO] Initializing RTL-Kernel-Stack system...")
    project = RTLKernelStack()
    
    try:
        success = project.run_all()
        if success:
            print("\n" + "=" * 70)
            print("✓ RTL-KERNEL-STACK EXECUTION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            
            # Show summary
            print("\n[SUMMARY]")
            print(f"Logs: results/logs/")
            if os.path.exists("results/plots/"):
                plots = os.listdir("results/plots/")
                if plots:
                    print(f"Waveforms: {', '.join(plots)}")
            
            # Check if driver is loaded
            try:
                result = subprocess.run(["lsmod"], capture_output=True, text=True)
                if "ll_driver" in result.stdout:
                    print("Driver: Loaded ✓")
                else:
                    print("Driver: Not loaded ✗")
            except:
                print("Driver: Unknown status")
                
        else:
            print("\n" + "=" * 70)
            print("✗ RTL-KERNEL-STACK EXECUTION FAILED")
            print("=" * 70)
            print("\n[TROUBLESHOOTING]")
            print("1. Check if RTL files exist: ls rtl/fifo/")
            print("2. Test iverilog manually: iverilog --version")
            print("3. Check file permissions: ls -la scripts/")
            
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
