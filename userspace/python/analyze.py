#!/usr/bin/env python3
# userspace/python/analyze.py
import sys
import os

def analyze_log(path):
    """Analyze simulation log files"""
    try:
        with open(path, "r") as f:
            results = []
            for line in f:
                if not line.strip():  # skip empty lines
                    continue
                
                # Look for test results in various formats
                if "data_in" in line and "data_out" in line:
                    # Parse lines like: "data_in=41 data_out=41"
                    parts = line.strip().split()
                    record = {}
                    for part in parts:
                        if '=' in part:
                            key, value = part.split('=')
                            try:
                                record[key] = int(value)
                            except ValueError:
                                record[key] = value  # keep as string if not int
                    if record:  # only add if we found data
                        results.append(record)
                
                # Alternative format: look for write/read patterns
                elif "Write:" in line or "Read:" in line:
                    # Parse lines like: "Write: data_in=41, full=0"
                    line = line.strip()
                    if "Write:" in line:
                        prefix = "Write:"
                    elif "Read:" in line:
                        prefix = "Read:"
                    else:
                        continue
                    
                    # Extract the data part
                    data_str = line.split(prefix)[1].strip()
                    parts = data_str.split(',')
                    record = {"type": prefix.replace(":", "").lower()}
                    
                    for part in parts:
                        part = part.strip()
                        if '=' in part:
                            key, value = part.split('=')
                            try:
                                record[key.strip()] = int(value.strip())
                            except ValueError:
                                record[key.strip()] = value.strip()
                    results.append(record)
        
        return results
    
    except FileNotFoundError:
        print(f"File {path} not found, run simulation first", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error analyzing log: {e}", file=sys.stderr)
        return []

def main():
    # Try different possible log file locations
    possible_paths = [
        "results/logs/fifo.log",
        "results/logs/fifo_test.log",
        "fifo.log",
        "../results/logs/fifo.log"
    ]
    
    data = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found log file: {path}")
            data = analyze_log(path)
            if data:
                break
    
    if not data:
        print("No simulation log files found or no data in logs.")
        print("Running simulation first...")
        return
    
    # Print analysis results
    print("\n" + "="*60)
    print("RTL SIMULATION ANALYSIS")
    print("="*60)
    
    # Count test types
    write_tests = [d for d in data if d.get('type') == 'write' or 'data_in' in d]
    read_tests = [d for d in data if d.get('type') == 'read' or 'data_out' in d]
    
    print(f"\nTotal test records: {len(data)}")
    print(f"Write operations: {len(write_tests)}")
    print(f"Read operations: {len(read_tests)}")
    
    # Show detailed results
    if write_tests or read_tests:
        print("\nDetailed Results:")
        print("-"*40)
        
        for i, record in enumerate(data[:10]):  # Show first 10 records
            if 'data_in' in record and 'data_out' in record:
                print(f"Test {i+1}: in={record['data_in']:3d} out={record['data_out']:3d} "
                      f"(hex: 0x{record['data_in']:02X} -> 0x{record['data_out']:02X})")
            elif 'data_in' in record:
                print(f"Write {i+1}: data_in={record['data_in']} full={record.get('full', 'N/A')}")
            elif 'data_out' in record:
                print(f"Read {i+1}: data_out={record['data_out']} empty={record.get('empty', 'N/A')}")
    
    # Calculate statistics if we have enough data
    if len(data) >= 2:
        print("\nStatistics:")
        print("-"*40)
        
        # Check for data integrity
        mismatches = 0
        for record in data:
            if 'data_in' in record and 'data_out' in record:
                if record['data_in'] != record['data_out']:
                    mismatches += 1
        
        if 'data_in' in data[0] and 'data_out' in data[0]:
            print(f"Data integrity: {len(data)-mismatches}/{len(data)} correct")
            if mismatches > 0:
                print(f"WARNING: {mismatches} data mismatches detected!")
        
        # Calculate timing if available
        timing_data = [d for d in data if 'time' in str(d).lower()]
        if timing_data:
            print(f"Timing measurements: {len(timing_data)} records")

if __name__ == "__main__":
    main()
