import os
import re

replacements = {
    r"Al-Muhandis \(المهندس\)": "TENSOR (The Strategist)",
    r"Al-Munafeedh \(المنفذ\)": "KINETIC (The Executor)",
    r"Al-Hakam \(الحکم\)": "AEGIS (The Overseer)", # Note the different character sometimes used for Hakam
    r"Al-Hakam \(الحكم\)": "AEGIS (The Overseer)",
    r"Al-Hafiz \(الحافظ\)": "LATTICE (The Memory)",
    r"Al-Burhan \(البرهان\)": "TOKAMAK (The Validator)",
    r"Al-Muhandis": "TENSOR",
    r"Al-Munafeedh": "KINETIC",
    r"Al-Hakam": "AEGIS",
    r"Al-Hafiz": "LATTICE",
    r"Al-Burhan": "TOKAMAK",
    r"AL-BURHAN": "TOKAMAK",
    r"DAREE3": "MEISSNER",
    r"SIYAADA": "ABLATION",
    r"SIYADA": "ABLATION",
    r"Mithaq": "Cherenkov",
    r"mithaq": "cherenkov",
    r"MITHAQ": "CHERENKOV",
    r"mithaq-professional": "cherenkov-professional"
}

def align_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for pattern, replacement in replacements.items():
            new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)
        
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
                if align_file(file_path):
                    count += 1
                    print(f"Aligned: {file_path}")
    
    print(f"Total documentation files aligned: {count}")

if __name__ == "__main__":
    main()
