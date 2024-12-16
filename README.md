# FreeRTOS Configuration

Provides a convenient way to add and remove tasks from the FreeRTOS build.
Based on [Embedded Software Design](https://www.beningo.com/embedded-software-design/) book.


## Usage

The task configuration file is a YAML file that defines the tasks to be created in FreeRTOS.
Upon building the project, a task_config.hh and task_config.cc file will be generated based on the task configuration file.

### Task Configuration File

Update the yaml file to include the tasks you want to create. The yaml file should have the following format:

```yaml

---
Task1:
  TaskName: "RGB_Task"
  TaskEntryPtr: "rgb_task"
  PeriodicityInMS: 33
  ParametersPtr: 0
  StackSize: STACK_SIZE_MEDIUM
  TaskPriority: 2
  TaskHandle: "nullptr"
  Core: "M4"

Task2:
    TaskName: "UART_Task"
    TaskEntryPtr: "uart_task"
    PeriodicityInMS: 33
    ParametersPtr: 0
    StackSize: STACK_SIZE_MEDIUM
    TaskPriority: 2
    TaskHandle: "nullptr"
    Core: "M7"

```

### Implementation

Create a task header and source file with the same name used in the yaml and a pointer to the parameter struct as the only argument.
For example with th rgb task we would have:
```cpp
// File: rgb_task.hh

#pragma once

void rgb_task(void* parameters);

```


## Build

Update your CMakeLists.txt file to include the following:

```cmake
# Define paths for task configuration
set(TASK_CONFIG_YAML "${CMAKE_CURRENT_SOURCE_DIR}/freertos_task_config_generator/tasks_config.yaml")
set(TASK_CONFIG_HEADER "${CMAKE_CURRENT_SOURCE_DIR}/include/task_config.hh")
set(TASK_CONFIG_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/task_config.cc")
set(TASK_GENERATOR_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/freertos_task_config_generator/generate_tasks.py")

# Define task source files for each core
set(M7_TASK_SOURCES
)

set(M4_TASK_SOURCES
    src/rgb_task.cc
)

# Add custom command to generate task configuration
add_custom_command(
    OUTPUT ${TASK_CONFIG_HEADER} ${TASK_CONFIG_SOURCE}
    COMMAND python3 ${TASK_GENERATOR_SCRIPT} 
            ${TASK_CONFIG_YAML} 
            ${TASK_CONFIG_HEADER} 
            ${TASK_CONFIG_SOURCE}
    DEPENDS ${TASK_CONFIG_YAML} ${TASK_GENERATOR_SCRIPT}
    COMMENT "Generating task configuration files"
    VERBATIM
)

# Create a custom target for task configuration generation
add_custom_target(${PROJECT_NAME}_generate_task_config
    DEPENDS ${TASK_CONFIG_HEADER} ${TASK_CONFIG_SOURCE}
)

# M4 Core Executable
add_executable_m4(${PROJECT_NAME}_m4
    src/main_m4.cc
    ${TASK_CONFIG_SOURCE}
    ${M4_TASK_SOURCES}
)
'''


##  Notes

Primarily tested on Coral Micro development board. Can't guarantee functionality on other boards or developments.