import os
import re

def remove_arabic_script(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove Arabic script characters
        # Range: \u0600-\u06FF (Arabic), \u0750-\u077F (Arabic Supplement)
        # \u08A0-\u08FF (Arabic Extended-A)
        new_content = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', '', content)
        
        # Clean up specific table column if it was "Arabic Translation"
        new_content = new_content.replace('Arabic Translation', 'Node Designation')
        
        # Clean up empty parentheses that might be left over from "Arabic (English)"
        new_content = new_content.replace('()', '')
        # Clean up double spaces
        new_content = re.sub(r' +', ' ', new_content)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return False

def main():
    docs_dir = 'c:/Users/moaid/mithaq-professional/docs'
    count = 0
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                if remove_arabic_script(file_path):
                    count += 1
                    print(f"Removed Arabic from: {file_path}")
    
    print(f"Total documentation files cleaned of Arabic script: {count}")

if __name__ == "__main__":
    main()
