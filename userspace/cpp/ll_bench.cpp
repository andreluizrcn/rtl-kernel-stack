// userspace/c/ll_raw_test.c - Enhanced version
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define DEVICE_PATH "/dev/ll_driver"
#define TEST_ITERATIONS 100

struct timespec t_start, t_end;

void print_hex(const char *label, uint32_t value) {
  printf("%s: 0x%08X\n", label, value);
}

int test_single_iteration(int iteration) {
  int fd;
  uint32_t buf = 0xAABBCCDD + iteration; // Different data each iteration
  size_t nbytes = sizeof(buf);
  ssize_t ret;
  long latency_ns;
  uint32_t read_buf = 0;

  // Open device
  fd = open(DEVICE_PATH, O_RDWR | O_NONBLOCK);
  if (fd < 0) {
    perror("open");
    return -1;
  }

  // Start timing
  if (clock_gettime(CLOCK_MONOTONIC, &t_start) != 0) {
    perror("clock_gettime start");
    close(fd);
    return -1;
  }

  // Write to device
  ret = write(fd, &buf, nbytes);
  if (ret < 0) {
    perror("write");
    close(fd);
    return -1;
  }

  // Read from device (with timeout)
  int attempts = 0;
  const int max_attempts = 1000;
  do {
    ret = read(fd, &read_buf, nbytes);
    attempts++;
    if (attempts > max_attempts) {
      printf("Timeout waiting for read\n");
      close(fd);
      return -1;
    }
    // Small delay to avoid busy looping too aggressively
    if (ret < 0 && errno == EAGAIN) {
      struct timespec ts = {0, 1000}; // 1 microsecond
      nanosleep(&ts, NULL);
    }
  } while (ret < 0 && errno == EAGAIN);

  if (ret < 0) {
    perror("read");
    close(fd);
    return -1;
  }

  // End timing
  if (clock_gettime(CLOCK_MONOTONIC, &t_end) != 0) {
    perror("clock_gettime end");
    close(fd);
    return -1;
  }

  // Close device
  close(fd);

  // Calculate latency
  latency_ns = (t_end.tv_sec - t_start.tv_sec) * 1000000000L +
               (t_end.tv_nsec - t_start.tv_nsec);

  // Verify data
  if (buf != read_buf) {
    printf("ERROR: Data mismatch! Written: 0x%08X, Read: 0x%08X\n", buf,
           read_buf);
    return -1;
  }

  return (int)latency_ns;
}

int main() {
  printf("RTL-Kernel-Stack Userspace Test\n");
  printf("===============================\n\n");

  long total_latency = 0;
  int successful_tests = 0;
  int failed_tests = 0;
  long min_latency = 1000000000L; // 1 second
  long max_latency = 0;

  for (int i = 0; i < TEST_ITERATIONS; i++) {
    printf("Test %3d/%d: ", i + 1, TEST_ITERATIONS);

    int latency = test_single_iteration(i);

    if (latency >= 0) {
      printf("Latency: %6d ns\n", latency);
      total_latency += latency;
      successful_tests++;

      if (latency < min_latency)
        min_latency = latency;
      if (latency > max_latency)
        max_latency = latency;
    } else {
      printf("FAILED\n");
      failed_tests++;
    }
  }

  printf("\n===============================\n");
  printf("Test Summary:\n");
  printf("  Successful tests: %d/%d\n", successful_tests, TEST_ITERATIONS);
  printf("  Failed tests:     %d\n", failed_tests);

  if (successful_tests > 0) {
    double avg_latency = (double)total_latency / successful_tests;
    printf("\nLatency Statistics:\n");
    printf("  Average: %.2f ns\n", avg_latency);
    printf("  Minimum: %ld ns\n", min_latency);
    printf("  Maximum: %ld ns\n", max_latency);
    printf("  Range:   %ld ns\n", max_latency - min_latency);

    // Convert to microseconds and milliseconds for readability
    printf("\nAlternative units:\n");
    printf("  Average: %.3f μs\n", avg_latency / 1000.0);
    printf("  Average: %.6f ms\n", avg_latency / 1000000.0);
  }

  return (failed_tests > 0) ? 1 : 0;
}
