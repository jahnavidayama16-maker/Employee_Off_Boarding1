import os
import zipfile

def package_project():
    project_dir = r"C:\Users\Jahnavi\.gemini\antigravity\scratch\hr_offboarding_system"
    zip_path = r"C:\Users\Jahnavi\.gemini\antigravity\scratch\hr_offboarding_viva_submission.zip"
    
    # Files and folders to exclude as requested (Unprofessional for production/distribution)
    excludes = ['venv', 'db.sqlite3', '.env', '__pycache__', '.git', 'package_project.py']
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Exclude folders
            dirs[:] = [d for d in dirs if d not in excludes and not d.startswith('.')]
            
            for file in files:
                if file in excludes or file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)
                
    print(f"Successfully packaged clean professional project to: {zip_path}")

if __name__ == "__main__":
    package_project()
