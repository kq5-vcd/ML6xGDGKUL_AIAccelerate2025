"""
File download and cleanup utilities.
"""

import os
import requests
from typing import Tuple, Optional

# Default download directory in the repo
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DOWNLOADS_DIR = os.path.join(REPO_ROOT, 'downloads')


def download_file(url: str, save_dir: Optional[str] = None, filename: Optional[str] = None) -> Tuple[bool, str]:
    """
    Downloads a file from a URL and saves it locally.
    
    Args:
        url: The URL to download the file from
        save_dir: Directory to save the file (defaults to repo downloads/)
        filename: Optional filename. If not provided, extracts from URL
        
    Returns:
        Tuple of (success: bool, message: str)
        - If successful: (True, absolute_file_path)
        - If failed: (False, error_message)
    """
    try:
        save_dir = save_dir or DOWNLOADS_DIR
        safe_save_dir = os.path.abspath(save_dir)
        os.makedirs(safe_save_dir, exist_ok=True)
        
        if filename is None:
            filename = url.split('/')[-1].split('?')[0]
            if not filename:
                filename = "downloaded_file"
        
        file_path = os.path.join(safe_save_dir, filename)
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return True, file_path
        else:
            return False, f"ERROR: File was not created or is empty: {file_path}"
            
    except requests.exceptions.RequestException as e:
        return False, f"ERROR: Network error during download: {type(e).__name__} - {e}"
    except OSError as e:
        return False, f"ERROR: File system error: {type(e).__name__} - {e}"
    except Exception as e:
        return False, f"ERROR: Unexpected error during download: {type(e).__name__} - {e}"


def remove_file(file_path: str) -> Tuple[bool, str]:
    """
    Safely removes a file from the filesystem.
    
    Args:
        file_path: Path to the file to remove
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        safe_file_path = os.path.abspath(file_path)
        
        if not os.path.exists(safe_file_path):
            return False, f"ERROR: File not found at path: {safe_file_path}"
        
        if not os.path.isfile(safe_file_path):
            return False, f"ERROR: Path is not a file: {safe_file_path}"
        
        os.remove(safe_file_path)
        
        if not os.path.exists(safe_file_path):
            return True, f"SUCCESS: File removed: {safe_file_path}"
        else:
            return False, f"ERROR: File still exists after removal attempt: {safe_file_path}"
            
    except PermissionError:
        return False, f"ERROR: Permission denied when trying to remove: {safe_file_path}"
    except OSError as e:
        return False, f"ERROR: File system error during removal: {type(e).__name__} - {e}"
    except Exception as e:
        return False, f"ERROR: Unexpected error during removal: {type(e).__name__} - {e}"

if __name__ == "__main__":
    print(download_file("https://github.com/GDG-KUL/ML6xGDGKUL_AIAccelerate2025/blob/main/benchmark/attachments/12.pdf"))