# FreeRTOS Configuration

Provides a convenient way to add and remove tasks from the FreeRTOS build.
Based on [Embedded Software Design](https://www.beningo.com/embedded-software-design/) book.



## Usage

The task configuration file is a YAML file that defines the tasks to be created in FreeRTOS.
Upon building the project, a task_config.hh and task_config.cc file will be generated based on the task configuration file.


## Build

Update your CMakeLists.txt file to include the following:

```cmake

# Define paths for task configuration
set(TASK_CONFIG_YAML "${CMAKE_CURRENT_SOURCE_DIR}/freertos_task_config_generator/tasks_config.yaml")
set(TASK_CONFIG_HEADER "${CMAKE_CURRENT_SOURCE_DIR}/include/task_config.hh")
set(TASK_CONFIG_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/task_config.cc")
set(TASK_GENERATOR_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/freertos_task_config_generator/generate_tasks.py")

# Define task source files
set(TASK_SOURCES
    // Add your task source files here
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
'''

Add any src files to the TASK_SOURCES list.

Include the task configuration files in the executable target. For example:

```cmake

# Add the executable and make it depend on task configuration
add_executable_m7(${PROJECT_NAME}
    src/main_cm7.cc
    ${TASK_CONFIG_SOURCE}
    ${TASK_SOURCES}
)

```

##  Notes

Primarily tested on Coral Micro development board. Can't guarantee functionality on other boards or developments.