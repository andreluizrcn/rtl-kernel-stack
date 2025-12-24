#include <chrono>
#include <iostream>
#include <vector>

int main() {
  // SETUP
  std::vector<int> data(1024, 1);
  int sum = 0;

  // WARM-UP
  for (int i = 0; i < data.size(); i++) {
    sum += data[i % data.size()];
  }

  // MEASURE
  auto start = std::chrono::high_resolution_clock::now();
  for (int i = 0; i < 10000000; i++) {
    sum += data[i % data.size()];
  }
  auto end = std::chrono::high_resolution_clock::now();

  auto total_time =
      std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();

  // RESULT
  std::cout << "Total time: " << total_time << " ns\n";
  std::cout << "Time per op: " << (double)total_time / 10000000 << " ns/op\n";

  return 0;
}
