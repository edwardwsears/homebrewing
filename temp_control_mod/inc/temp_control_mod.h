#include <linux/mutex.h>

//
// temp_control_mod.h
//
// Contains common structures and defines for the temp_control module
//

#ifdef _TEMP_CONTROL_MOD_H_
#else
#define _TEMP_CONTROL_MOD_H_

#define PRINT_TEMP_CONTROL(_format, ...) printk(KERN_INFO "TEMP_CONTROL: " _format "\n", ##__VA_ARGS__)

#define LOCK_OBJ() mutex_lock(&temp_control.obj_mutex);
#define UNLOCK_OBJ() mutex_unlock(&temp_control.obj_mutex);

struct temp_control
{
    int set_temp;
    int set_range;
    struct mutex obj_mutex;
};

#endif
