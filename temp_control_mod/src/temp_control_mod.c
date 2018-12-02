#include <linux/init.h>
#include <linux/module.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/string.h>

#include "temp_control_mod.h"
#include "temp_control_sysfs.h"
#include "temp_control_thread.h"

MODULE_LICENSE("GPL");

struct temp_control temp_control;

//
// MODULE
//

static int __init temp_control_init(void){
    PRINT_TEMP_CONTROL("staring...");
    temp_control_sysfs_init();

    //initialize object settings
    mutex_init(&temp_control.obj_mutex);
    LOCK_OBJ();
    temp_control.set_temp  = 20;
    temp_control.set_range = 1;
    UNLOCK_OBJ();

    temp_control_thread_init();

    PRINT_TEMP_CONTROL("staring done.");
    return 0;
}

static void __exit temp_control_exit(void){
    PRINT_TEMP_CONTROL("stopping...");
    temp_control_sysfs_exit();
    temp_control_thread_exit();
    PRINT_TEMP_CONTROL("stopping done.");
}

module_init(temp_control_init);
module_exit(temp_control_exit);
