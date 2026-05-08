import os
import re

def replace_in_file(file_path, search_text, replace_text):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Case insensitive replacement for 'cherenkov' to 'cherenkov'
        # But specifically targeting 'cherenkov-professional' first
        new_content = content.replace('cherenkov-professional', 'cherenkov-professional')
        new_content = new_content.replace('CHERENKOV-PROFESSIONAL', 'CHERENKOV-PROFESSIONAL')
        new_content = new_content.replace('cherenkov', 'cherenkov')
        new_content = new_content.replace('Cherenkov', 'Cherenkov')
        new_content = new_content.replace('CHERENKOV', 'CHERENKOV')
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return False

def main():
    root_dir = 'c:/Users/moaid/cherenkov-professional'
    exclude_dirs = {'.git', 'venv', '.venv', '__pycache__', 'cherenkov-frontend', 'cherenkov-portal'}
    
    count = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.sh', '.yml', '.yaml', '.json', '.html', '.css', '.js', 'Dockerfile', 'pyproject.toml')):
                file_path = os.path.join(root, file)
                if replace_in_file(file_path, 'cherenkov', 'cherenkov'):
                    count += 1
                    print(f"Updated: {file_path}")
    
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    main()
