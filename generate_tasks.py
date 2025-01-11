#!/usr/bin/env python3

import yaml
import sys
import os
from datetime import date

def generate_core_header(core):
    return f"""// AUTO-GENERATED FILE BY "scripts/generate_tasks.py" 
// EDIT AT YOUR OWN RISK.

#pragma once

#include "third_party/freertos_kernel/include/FreeRTOS.h"
#include "third_party/freertos_kernel/include/task.h"

#include <cstdio>

namespace coralmicro {{

// Task priorities (configMAX_PRIORITIES = 5)
constexpr int TASK_PRIORITY_HIGH   = (configMAX_PRIORITIES - 1);  // 4
constexpr int TASK_PRIORITY_MEDIUM = (configMAX_PRIORITIES - 2);  // 3
constexpr int TASK_PRIORITY_LOW    = (configMAX_PRIORITIES - 3);  // 2

// Stack sizes
constexpr int STACK_SIZE_LARGE  = (configMINIMAL_STACK_SIZE * 4);  // 1440 bytes
constexpr int STACK_SIZE_MEDIUM = (configMINIMAL_STACK_SIZE * 3);  // 1080 bytes
constexpr int STACK_SIZE_SMALL  = (configMINIMAL_STACK_SIZE * 2);  // 720 bytes

// Task interface
enum class TaskErr_t {{
    OK = 0,
    CREATE_FAILED,
}};

// Function to create tasks for {core} core
TaskErr_t Create{core}Tasks();

}} // namespace coralmicro"""

def generate_core_source(tasks, core, header_filepath, header_prefix=None):
    # Collect task headers for this core
    task_headers = set()
    core_tasks = {}

    # Extract filepath after "include" string, if it exists
    # If it does, then get directory in whihc the header file is goiung to be generated and use that as prepix for task includes
    try:
        header_filepath = header_filepath.split("include/")[1].strip()
    
    except Exception as e:
        pass
    
    if not header_prefix:
        for task_name, task in tasks.items():
            if task.get('Core') == core:
                task_name = task['TaskEntryPtr'].replace("_task", "")
                task_headers.add(f"#include \"{task_name}_task.hh\"")
                core_tasks[task_name] = task
        
        header_includes = "\n".join(sorted(task_headers))

    else:
        for task_name, task in tasks.items():
            if task.get('Core', 'M7') == core:
                task_name = task['TaskEntryPtr'].replace("_task", "")
                task_headers.add(f"#include \"{header_prefix}/{task_name}_task.hh\"")
                core_tasks[task_name] = task
        
        header_includes = "\n".join(sorted(task_headers))



    config_entries = []
    for task_name, task in core_tasks.items():
        entry = f"""    {{
        {task['TaskEntryPtr']},
        "{task['TaskName']}",
        {task['StackSize']},
        {task['ParametersPtr']},
        {task['TaskPriority']},
        {task['TaskHandle']}
    }}"""
        config_entries.append(entry)

    config_string = ",\n".join(config_entries)

    return f"""// AUTO-GENERATED FILE FROM "scripts/generate_tasks.py"
// EDIT AT YOUR OWN RISK.

#include "{header_filepath}"
#include <string.h>

// Task implementations
{header_includes}

namespace coralmicro {{
namespace {{

struct TaskConfig {{
    TaskFunction_t taskFunction;
    const char* taskName;
    uint32_t stackSize;
    void* parameters;
    UBaseType_t priority;
    TaskHandle_t* handle;
}};

constexpr TaskConfig k{core}TaskConfigs[] = {{
{config_string}
}};

}} // namespace

TaskErr_t Create{core}Tasks() {{
    TaskErr_t status = TaskErr_t::OK;

    for (const auto& config : k{core}TaskConfigs) {{
        BaseType_t ret = xTaskCreate(
            config.taskFunction,
            config.taskName,
            config.stackSize,
            config.parameters,
            config.priority,
            config.handle
        );

        if (ret != pdPASS) {{
            printf("Failed to create {core} task: %s\\r\\n", config.taskName);
            status = TaskErr_t::CREATE_FAILED;
            break;
        }}
        
        printf("Created {core} task: %s\\r\\n", config.taskName);
    }}

    return status;
}}

}} // namespace coralmicro"""

def main():
    if len(sys.argv) > 8 or len(sys.argv) < 6:
        print("Usage: generate_tasks.py <yaml_file> <m7_header> <m7_source> <m4_header> <m4_source> \n optional: [m7_header_prefix] [m4_header_prefix]")
        sys.exit(1)

    # We have at least 5 arguments, but may have 6 or 7
    if len(sys.argv) == 6:
        yaml_filepath = sys.argv[1]
        m7_header_filepath = sys.argv[2]
        m7_source_filepath = sys.argv[3]
        m4_header_filepath = sys.argv[4]
        m4_source_filepath = sys.argv[5]

        m7_header_filepath_prefix = None
        m4_header_filepath_prefix = None

    elif len(sys.argv) == 7:
        yaml_filepath = sys.argv[1]
        m7_header_filepath = sys.argv[2]
        m7_source_filepath = sys.argv[3]
        m4_header_filepath = sys.argv[4]
        m4_source_filepath = sys.argv[5]

        m7_header_filepath_prefix  = sys.argv[6]
        m4_header_filepath_prefix = None

    elif len(sys.argv) == 8:
        yaml_filepath = sys.argv[1]
        m7_header_filepath = sys.argv[2]
        m7_source_filepath = sys.argv[3]
        m4_header_filepath = sys.argv[4]
        m4_source_filepath = sys.argv[5]

        m7_header_filepath_prefix  = sys.argv[6]
        m4_header_filepath_prefix = sys.argv[7]


    try:
        with open(yaml_filepath, 'r') as stream:
            tasks = yaml.safe_load(stream)

        # Create directories if they don't exist
        for filepath in [m7_header_filepath, m7_source_filepath, 
                        m4_header_filepath, m4_source_filepath]:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Generate and write M7 files
        with open(m7_header_filepath, 'w') as f:
            f.write(generate_core_header("M7"))
        with open(m7_source_filepath, 'w') as f:
            f.write(generate_core_source(tasks, "M7", m7_header_filepath, m7_header_filepath_prefix))

        # Generate and write M4 files
        with open(m4_header_filepath, 'w') as f:
            f.write(generate_core_header("M4"))
        with open(m4_source_filepath, 'w') as f:
            f.write(generate_core_source(tasks, "M4", m4_header_filepath, m4_header_filepath_prefix))

    except Exception as e:
        print(f"Error generating task configuration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()