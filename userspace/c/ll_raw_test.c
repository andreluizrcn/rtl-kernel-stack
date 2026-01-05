#include <asm-generic/errno-base.h>
#include <errno.h>  // errno
#include <fcntl.h>  // open, O_*
#include <stdint.h> // uint32_t
#include <stdio.h>  // printf, perror
#include <time.h>
#include <unistd.h> // write, close

struct timespec t_start, t_end;

int main() {
  int fd;
  uint32_t buf = 0xAABBCCDD;
  size_t nbytes = sizeof(buf);
  ssize_t ret;
  ssize_t bytes_read;
  long latency_ns;

  // OPEN = (PATHNAME | FLAGS | MODE)
  fd = open("/dev/ll_driver", O_RDWR | O_NONBLOCK);
  if (fd < 0) {
    perror("open");
    return 1;
  } else {
    printf("Device opened, fd=%d\n", fd);
  }

  // TIME GET START
  clock_gettime(CLOCK_MONOTONIC, &t_end);

  // WRITE
  ret = write(fd, &buf, nbytes);
  if (ret < 0) {
    perror("write");
    close(fd);
    return 1;
  } else {
    printf("write OK: %zd bytes written\n", ret);
  }

  // READ
  // #TODO: change this busy wait loop in the future
  do {
    bytes_read = read(fd, &buf, nbytes);
  } while (bytes_read < 0 && errno == EAGAIN);

  // TIME GET END
  clock_gettime(CLOCK_MONOTONIC, &t_end);

  // CLOSE
  close(fd);

  // LATENCY
  latency_ns = (t_end.tv_sec - t_start.tv_sec) * 1000000000L +
               (t_end.tv_nsec - t_start.tv_nsec);

  printf("Latency: %ld ns\n", latency_ns);
  return 0;
}
