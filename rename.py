import os
import re

files = [
    'README.md', 'docs/API.md', '.env.example', 'src/logger.py', 
    'test_architecture.py', 'src/context_manager.py', 'src/execution_manager.py', 
    'src/memory_manager.py', 'src/planner.py', 'src/security.py', 
    'src/executors/base_executor.py', 'src/executors/dev_executor.py', 
    'src/executors/pyautogui_executor.py', 'src/executors/student_executor.py', 
    'src/executors/ui_automation_executor.py', 'ui/android.html', 
    'ui/index_backup.html', 'buildozer.spec'
]

for filepath in files:
    if not os.path.exists(filepath): 
        continue
    with open(filepath, 'r', encoding='utf-8') as f: 
        content = f.read()
    
    new_content = re.sub(r'Servent-AI', 'Forge', content, flags=re.IGNORECASE)
    new_content = re.sub(r'ServentAI', 'Forge', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'Servent AI', 'Forge', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'Servent', 'Forge', new_content)
    new_content = re.sub(r'servent', 'forge', new_content)
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f: 
            f.write(new_content)
        print(f'Updated {filepath}')
