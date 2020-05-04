#include <linux/init.h>
#include <linux/module.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/string.h>

#include "temp_control_mod.h"
#include "temp_control_sysfs.h"

MODULE_LICENSE("GPL");

//
// temp_control_sysfs.c
//
// Contains sysfs nodes to:
// 1. control module settings
// 2. read status and history
//

extern struct temp_control temp_control;
static struct kobject *temp_control_kobject;

//
// Set Temp
//

static ssize_t set_temp_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);
static ssize_t set_temp_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count);

static struct kobj_attribute set_temp_attribute =__ATTR(set_temp, (S_IWUSR | S_IRUGO), set_temp_show, set_temp_store);

static ssize_t set_temp_show(struct kobject *kobj, struct kobj_attribute *attr,
                      char *buf)
{
    ssize_t set_temp;
    LOCK_OBJ();
    set_temp = sprintf(buf, "%d\n", temp_control.set_temp);
    UNLOCK_OBJ();
    return set_temp;
}

static ssize_t set_temp_store(struct kobject *kobj, struct kobj_attribute *attr,
                      const char *buf, size_t count)
{
    LOCK_OBJ();
    sscanf(buf, "%du", &temp_control.set_temp);
    PRINT_TEMP_CONTROL("Changing Set Temperature: %dF",temp_control.set_temp);
    UNLOCK_OBJ();
    return count;
}

//
// Set range
//

static ssize_t set_range_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);
static ssize_t set_range_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count);

static struct kobj_attribute set_range_attribute =__ATTR(set_range, (S_IWUSR | S_IRUGO), set_range_show, set_range_store);

static ssize_t set_range_show(struct kobject *kobj, struct kobj_attribute *attr,
                      char *buf)
{
    LOCK_OBJ();
    return sprintf(buf, "%d\n", temp_control.set_range);
    UNLOCK_OBJ();
}

static ssize_t set_range_store(struct kobject *kobj, struct kobj_attribute *attr,
                      const char *buf, size_t count)
{
    LOCK_OBJ();
    sscanf(buf, "%du", &temp_control.set_range);
    PRINT_TEMP_CONTROL("Changing allowable temperature range: %dF",temp_control.set_range);
    UNLOCK_OBJ();
    return count;
}

//
// Current Temp
//

static ssize_t current_temp_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);

static struct kobj_attribute current_temp_attribute =__ATTR(current_temp, (S_IWUSR | S_IRUGO), current_temp_show, NULL);

static ssize_t current_temp_show(struct kobject *kobj, struct kobj_attribute *attr,
                      char *buf)
{
    ssize_t current_temp;
    LOCK_OBJ();
    current_temp = sprintf(buf, "%d\n", temp_control.current_temp);
    UNLOCK_OBJ();
    return current_temp;
}

//
// Sysfs init/exit
//

void temp_control_sysfs_init(void){
    PRINT_TEMP_CONTROL("starting sysfs...");
    //create sysfs object
    temp_control_kobject = kobject_create_and_add("temp_control", NULL);

    // Add files
    if (sysfs_create_file(temp_control_kobject, &set_temp_attribute.attr)) {
        pr_debug("failed to create set_temp sysfs!\n");
    }
    if (sysfs_create_file(temp_control_kobject, &set_range_attribute.attr)) {
        pr_debug("failed to create set_range sysfs!\n");
    }
    if (sysfs_create_file(temp_control_kobject, &current_temp_attribute.attr)) {
        pr_debug("failed to create set_range sysfs!\n");
    }

    PRINT_TEMP_CONTROL("starting sysfs done");
}

void temp_control_sysfs_exit(void){
  PRINT_TEMP_CONTROL("stopping sysfs...");
  //remove sysfs object
  kobject_put(temp_control_kobject);
  PRINT_TEMP_CONTROL("stopping sysfs done");
}
