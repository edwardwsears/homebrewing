#include <linux/init.h>
#include <linux/module.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include "temp_control_mod.h"

extern struct temp_control temp_control;
#define THREAD_NAME "temp_control_thread"
struct task_struct *task;

int temp_control_thread(void *data){
  while(1) {
    LOCK_OBJ();
    PRINT_TEMP_CONTROL("Thread: set_temp = %d", temp_control.set_temp);
    PRINT_TEMP_CONTROL("Thread: set_range = %d", temp_control.set_range);
    UNLOCK_OBJ();
    usleep_range(1000, 1000);
    if (kthread_should_stop()) break;
  }
  return 0;
}

void temp_control_thread_init(void){
    PRINT_TEMP_CONTROL("Starting Thread...");
    task = kthread_run(temp_control_thread, NULL, THREAD_NAME);
    PRINT_TEMP_CONTROL("Starting Thread Done");
}

void temp_control_thread_exit(void){
    PRINT_TEMP_CONTROL("Stopping Thread...");
    kthread_stop(task);
    PRINT_TEMP_CONTROL("Stopping Thread Done");
}
