# genia_download_github.py
import urllib.request
import zipfile
import os
import shutil

def download_from_github():
    """Télécharge le corpus GENIA directement depuis GitHub"""
    
    print("Téléchargement du corpus GENIA depuis GitHub...")
    print("="*60)
    
    # URL du repository
    repo_url = "https://github.com/openbiocorpora/genia-term/archive/refs/heads/master.zip"
    
    # Créer dossier de destination
    os.makedirs("genia_data", exist_ok=True)
    zip_path = "genia_data/genia-term-master.zip"
    
    try:
        # Télécharger
        print("\n[1/3] Téléchargement...")
        urllib.request.urlretrieve(repo_url, zip_path)
        print(f"✓ Téléchargé: {zip_path}")
        
        # Extraire
        print("\n[2/3] Extraction...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("genia_data")
        print("✓ Fichiers extraits")
        
        # Lister les fichiers
        print("\n[3/3] Fichiers disponibles:")
        extracted_path = "genia_data/genia-term-master"
        
        for root, dirs, files in os.walk(extracted_path):
            for file in files:
                if file.endswith(('.xml', '.txt', '.a1', '.a2')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, "genia_data")
                    size = os.path.getsize(file_path) / 1024  # KB
                    print(f"  - {rel_path} ({size:.1f} KB)")
        
        print("\n" + "="*60)
        print("✓ SUCCÈS! Corpus GENIA téléchargé")
        print(f"✓ Dossier: {extracted_path}")
        print("="*60)
        
        return extracted_path
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    download_from_github()