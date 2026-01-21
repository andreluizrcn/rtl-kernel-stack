// kernel/ll_driver/ll_driver.c - FIXED VERSION
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/kernel.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/sched.h>
#include <linux/uaccess.h>
#include <linux/wait.h>

#define DEVICE_NAME "ll_driver"
#define CLASS_NAME "ll_class"

static int major_number;
static struct class *ll_class = NULL;
static struct device *ll_device = NULL;

// Mutex for concurrent access
static DEFINE_MUTEX(ll_mutex);
static DECLARE_WAIT_QUEUE_HEAD(ll_wait_queue);
static int data_ready = 0;

// Device data structure
struct ll_device_data {
  uint32_t buffer;
  ktime_t timestamp;
  int irq_enabled;
};

static struct ll_device_data dev_data;

// File operations
static int ll_open(struct inode *inodep, struct file *filep) {
  if (!mutex_trylock(&ll_mutex)) {
    printk(KERN_ALERT "RTL-KERNEL-STACK: Device in use\n");
    return -EBUSY;
  }
  printk(KERN_INFO "RTL-KERNEL-STACK: Device opened\n");
  return 0;
}

static int ll_release(struct inode *inodep, struct file *filep) {
  mutex_unlock(&ll_mutex);
  printk(KERN_INFO "RTL-KERNEL-STACK: Device closed\n");
  return 0;
}

static ssize_t ll_read(struct file *filep, char __user *buffer, size_t len,
                       loff_t *offset) {
  // Wait until data is ready
  if (filep->f_flags & O_NONBLOCK) {
    if (!data_ready)
      return -EAGAIN;
  } else {
    wait_event_interruptible(ll_wait_queue, data_ready);
  }

  // Copy data to userspace
  if (copy_to_user(buffer, &dev_data.buffer, sizeof(dev_data.buffer))) {
    return -EFAULT;
  }

  dev_data.timestamp = ktime_get_ns();
  data_ready = 0;

  return sizeof(dev_data.buffer);
}

static ssize_t ll_write(struct file *filep, const char __user *buffer,
                        size_t len, loff_t *offset) {
  if (len != sizeof(dev_data.buffer)) {
    return -EINVAL;
  }

  // Copy data from userspace
  if (copy_from_user(&dev_data.buffer, buffer, sizeof(dev_data.buffer))) {
    return -EFAULT;
  }

  printk(KERN_INFO "RTL-KERNEL-STACK: Received 0x%08x\n", dev_data.buffer);

  // Mark data as ready
  data_ready = 1;
  wake_up_interruptible(&ll_wait_queue);

  return sizeof(dev_data.buffer);
}

static long ll_ioctl(struct file *filep, unsigned int cmd, unsigned long arg) {
  switch (cmd) {
  case 0x01: // Get timestamp
    return copy_to_user((void __user *)arg, &dev_data.timestamp,
                        sizeof(dev_data.timestamp))
               ? -EFAULT
               : 0;
  default:
    return -ENOTTY;
  }
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = ll_open,
    .release = ll_release,
    .read = ll_read,
    .write = ll_write,
    .unlocked_ioctl = ll_ioctl,
};

static int __init ll_driver_init(void) {
  printk(KERN_INFO "RTL-KERNEL-STACK: Initializing...\n");

  // Allocate major number
  major_number = register_chrdev(0, DEVICE_NAME, &fops);
  if (major_number < 0) {
    printk(KERN_ALERT "Failed to register major number\n");
    return major_number;
  }

  // Create device class (FIXED: removed THIS_MODULE parameter)
  ll_class = class_create(CLASS_NAME);
  if (IS_ERR(ll_class)) {
    unregister_chrdev(major_number, DEVICE_NAME);
    printk(KERN_ALERT "Failed to create class\n");
    return PTR_ERR(ll_class);
  }

  // Create device
  ll_device =
      device_create(ll_class, NULL, MKDEV(major_number, 0), NULL, DEVICE_NAME);
  if (IS_ERR(ll_device)) {
    class_destroy(ll_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    printk(KERN_ALERT "Failed to create device\n");
    return PTR_ERR(ll_device);
  }

  // Initialize
  dev_data.buffer = 0;
  dev_data.timestamp = 0;
  dev_data.irq_enabled = 0;
  data_ready = 0;

  printk(KERN_INFO "RTL-KERNEL-STACK: Initialized with major %d\n",
         major_number);
  return 0;
}

static void __exit ll_driver_exit(void) {
  device_destroy(ll_class, MKDEV(major_number, 0));
  class_destroy(ll_class);
  unregister_chrdev(major_number, DEVICE_NAME);
  printk(KERN_INFO "RTL-KERNEL-STACK: Removed\n");
}

module_init(ll_driver_init);
module_exit(ll_driver_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("RTL-Kernel-Stack");
MODULE_DESCRIPTION("Low-Latency Driver");
MODULE_VERSION("1.0");
