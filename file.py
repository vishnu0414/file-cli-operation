#!/usr/bin/env python3
"""
File Operations CLI Tool
--------------------------------
Features:
- Create, Read, Write, Append files
- Rename and Delete files/folders
- Copy & Move files
- Search files by name, extension, or keyword
- Compress & Extract (.zip)
- Organize files by extension into categories
- Storage Analysis across drives
- Delete Temporary Files (optional yes/no)
- Dry-run support (preview actions)
- Interactive Menu Mode
- Loading effect for operations
- Compression suggestion for large files
- Works across drives (C:, D:, E:, etc.)
"""

import os
import sys
import shutil
import argparse
import zipfile
import platform
import tempfile
import time
import itertools
from pathlib import Path
from datetime import datetime

# ------------------- ICON DEFINITIONS ------------------- #
ICONS = {
    'create': '📝',
    'read': '📖',
    'write': '✍️',
    'append': '➕',
    'rename': '✏️',
    'delete': '🗑️',
    'copy': '📋',
    'move': '➡️',
    'search': '🔍',
    'compress': '📦',
    'extract': '📂',
    'organize': '📁',
    'storage': '💾',
    'success': '✔️',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'file': '📄',
    'folder': '📁',
    'image': '🖼️',
    'video': '🎬',
    'music': '🎵',
    'document': '📑',
    'program': '💻',
    'archive': '📦',
    'temp': '🗑️',
}

# ------------------- EXTENSION -> CATEGORY ------------------- #
EXTENSION_FOLDERS = {
    '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images', '.svg': 'Images',
    '.webp': 'Images', '.heic': 'Images',
    '.mp4': 'Videos', '.avi': 'Videos', '.mkv': 'Videos', '.mov': 'Videos', '.wmv': 'Videos',
    '.pdf': 'Documents', '.doc': 'Documents', '.docx': 'Documents',
    '.xls': 'Documents', '.xlsx': 'Documents', '.csv': 'Documents',
    '.ppt': 'Documents', '.pptx': 'Documents', '.txt': 'Documents',
    '.mp3': 'Music', '.wav': 'Music', '.aac': 'Music', '.flac': 'Music',
    '.py': 'Programs', '.ipynb': 'Programs', '.c': 'Programs', '.cpp': 'Programs',
    '.java': 'Programs', '.js': 'Programs', '.ts': 'Programs', '.sh': 'Programs',
    '.exe': 'Applications', '.msi': 'Applications', '.apk': 'Applications',
    '.dmg': 'Applications', '.deb': 'Applications', '.rpm': 'Applications',
    '.zip': 'Compressed', '.rar': 'Compressed', '.7z': 'Compressed',
    '.tar': 'Compressed', '.gz': 'Compressed'
}

# ------------------- LOADING BOX ------------------- #
def loading_effect(message="Processing", duration=2):
    colors = ["\033[94m", "\033[92m"]  # Blue & Green
    reset = "\033[0m"
    spinner = itertools.cycle(["▮", "▯"])
    t_end = time.time() + duration
    i = 0
    while time.time() < t_end:
        color = colors[i % len(colors)]
        sys.stdout.write(f"\r{color}{message} {next(spinner)}{reset}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.2)
    print("\r" + " " * 50)  # Clear the line

# ------------------- FILE OPERATIONS ------------------- #
def validate_path(path, should_exist=True, path_type='auto'):
    """
    Comprehensive path validation
    Args:
        path: Path to validate
        should_exist: Whether path should already exist
        path_type: 'file', 'dir', or 'auto' for automatic detection
    """
    if not path or not isinstance(path, str):
        return False, f"{ICONS['error']} Invalid path format - path must be a non-empty string"
    
    try:
        path = path.strip()
        if not path:
            return False, f"{ICONS['error']} Invalid path - cannot be empty or whitespace only"
        
        path_obj = Path(path)
        
        # Check for invalid characters in path
        invalid_chars = ['<', '>', '|', '\0', '\n', '\r']
        if any(char in str(path_obj) for char in invalid_chars):
            return False, f"{ICONS['error']} Invalid path - contains illegal characters"
        
        if should_exist:
            if not path_obj.exists():
                return False, f"{ICONS['error']} Path does not exist: {path}"
            
            # Type checking
            if path_type == 'file' and path_obj.is_dir():
                return False, f"{ICONS['error']} Expected file but found directory: {path}"
            elif path_type == 'dir' and path_obj.is_file():
                return False, f"{ICONS['error']} Expected directory but found file: {path}"
        else:
            # For new paths, check if parent directory exists
            parent = path_obj.parent
            if not parent.exists():
                return False, f"{ICONS['error']} Parent directory does not exist: {parent}"
            
            # Check if file already exists (for safety)
            if path_obj.exists() and path_type == 'file':
                return True, f"{ICONS['warning']} File already exists (will be overwritten)"
        
        return True, None
    except PermissionError:
        return False, f"{ICONS['error']} Permission denied - insufficient privileges for: {path}"
    except OSError as e:
        return False, f"{ICONS['error']} OS error - {str(e)}"
    except Exception as e:
        return False, f"{ICONS['error']} Invalid path format: {str(e)}"

def create_file(path):
    """Create a new file with comprehensive error handling"""
    valid, error = validate_path(path, should_exist=False, path_type='file')
    if not valid:
        print(error)
        return False
    
    try:
        path_obj = Path(path)
        
        # Ensure parent directory exists
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the file
        path_obj.touch(exist_ok=True)
        loading_effect("Creating file")
        print(f"{ICONS['success']} {ICONS['create']} Created file: {path}")
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot create file in this location")
        return False
    except IsADirectoryError:
        print(f"{ICONS['error']} Path is a directory, not a file: {path}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not create file: {str(e)}")
        return False

def read_file(path):
    """Read file contents with comprehensive error handling"""
    valid, error = validate_path(path, should_exist=True, path_type='file')
    if not valid:
        print(error)
        return False
    
    try:
        if not os.access(path, os.R_OK):
            print(f"{ICONS['error']} Permission denied - cannot read file: {path}")
            return False
        
        loading_effect("Reading file")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"\n{ICONS['read']} Content of {path}:")
            print("─" * 60)
            print(content if content else "[Empty file]")
            print("─" * 60)
        return True
    except UnicodeDecodeError:
        print(f"{ICONS['error']} Could not read file - encoding error (not UTF-8)")
        return False
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot read file: {path}")
        return False
    except IsADirectoryError:
        print(f"{ICONS['error']} Path is a directory, not a file: {path}")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} File not found: {path}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not read file: {str(e)}")
        return False

def write_file(path, text, append=False):
    """Write or append to file with comprehensive error handling"""
    valid, error = validate_path(path, should_exist=append, path_type='file')
    if not valid and append:
        print(error)
        return False
    
    try:
        if not text or not isinstance(text, str):
            print(f"{ICONS['warning']} Warning: text input appears invalid, writing empty content")
        
        # For new files, ensure parent directory exists
        if not append:
            path_obj = Path(path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        mode = "a" if append else "w"
        icon = ICONS['append'] if append else ICONS['write']
        
        if not os.access(Path(path).parent, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot write to this directory")
            return False
        
        loading_effect("Writing to file")
        with open(path, mode, encoding="utf-8") as f:
            f.write(text + "\n")
        
        action = "Appended to" if append else "Written to"
        print(f"{ICONS['success']} {icon} {action}: {path}")
        check_suggest_compress(path)
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot write to file")
        return False
    except IsADirectoryError:
        print(f"{ICONS['error']} Path is a directory, not a file: {path}")
        return False
    except IOError as e:
        print(f"{ICONS['error']} I/O error - could not write to file: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not write to file: {str(e)}")
        return False

def rename_item(src, dst):
    """Rename file or directory with comprehensive error handling"""
    valid_src, error_src = validate_path(src, should_exist=True)
    if not valid_src:
        print(error_src)
        return False
    
    if not dst or not isinstance(dst, str):
        print(f"{ICONS['error']} Destination path cannot be empty")
        return False
    
    dst = dst.strip()
    
    try:
        if Path(dst).exists():
            print(f"{ICONS['error']} Destination already exists: {dst}")
            return False
        
        # Check write permission on parent directory
        if not os.access(Path(dst).parent, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot write to destination directory")
            return False
        
        loading_effect("Renaming")
        os.rename(src, dst)
        print(f"{ICONS['success']} {ICONS['rename']} Renamed: {src} → {dst}")
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot rename item")
        return False
    except FileExistsError:
        print(f"{ICONS['error']} Destination already exists")
        return False
    except OSError as e:
        print(f"{ICONS['error']} OS error during rename: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not rename {src}: {e}")
        return False

def delete_item(path):
    """Delete file or directory with comprehensive error handling"""
    valid, error = validate_path(path, should_exist=True)
    if not valid:
        print(error)
        return False
    
    try:
        # Check if we have permission
        if not os.access(path, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot delete: {path}")
            return False
        
        loading_effect("Deleting")
        if os.path.isdir(path):
            # Check if directory is not empty
            if os.listdir(path) and not os.access(path, os.R_OK | os.W_OK | os.X_OK):
                print(f"{ICONS['error']} Permission denied - cannot delete non-empty directory")
                return False
            shutil.rmtree(path)
        else:
            os.remove(path)
        print(f"{ICONS['success']} {ICONS['delete']} Deleted: {path}")
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot delete item")
        return False
    except OSError as e:
        print(f"{ICONS['error']} OS error during delete: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not delete {path}: {str(e)}")
        return False

def copy_item(src, dst):
    """Copy file or directory with comprehensive error handling"""
    valid_src, error_src = validate_path(src, should_exist=True)
    if not valid_src:
        print(error_src)
        return False
    
    if not dst or not isinstance(dst, str):
        print(f"{ICONS['error']} Destination path cannot be empty")
        return False
    
    dst = dst.strip()
    
    try:
        # Check source readability
        if not os.access(src, os.R_OK):
            print(f"{ICONS['error']} Permission denied - cannot read source: {src}")
            return False
        
        # Create parent directory if needed
        dst_parent = Path(dst).parent
        if not dst_parent.exists():
            dst_parent.mkdir(parents=True, exist_ok=True)
        
        # Check destination write permission
        if not os.access(dst_parent, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot write to destination")
            return False
        
        loading_effect("Copying")
        if os.path.isdir(src):
            if os.path.exists(dst):
                print(f"{ICONS['warning']} Destination exists, merging contents")
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        print(f"{ICONS['success']} {ICONS['copy']} Copied: {src} → {dst}")
        check_suggest_compress(dst)
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot copy item")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} Source file not found: {src}")
        return False
    except IsADirectoryError:
        print(f"{ICONS['error']} Destination is a directory, not a file")
        return False
    except OSError as e:
        print(f"{ICONS['error']} OS error during copy: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not copy {src}: {str(e)}")
        return False

def move_item(src, dst):
    """Move file or directory with comprehensive error handling"""
    valid_src, error_src = validate_path(src, should_exist=True)
    if not valid_src:
        print(error_src)
        return False
    
    if not dst or not isinstance(dst, str):
        print(f"{ICONS['error']} Destination path cannot be empty")
        return False
    
    dst = dst.strip()
    
    try:
        # Check permissions
        if not os.access(src, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot move source")
            return False
        
        # Create parent directory if needed
        dst_parent = Path(dst).parent
        if not dst_parent.exists():
            dst_parent.mkdir(parents=True, exist_ok=True)
        
        if not os.access(dst_parent, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot write to destination")
            return False
        
        loading_effect("Moving")
        shutil.move(src, dst)
        print(f"{ICONS['success']} {ICONS['move']} Moved: {src} → {dst}")
        check_suggest_compress(dst)
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot move item")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} Source not found: {src}")
        return False
    except OSError as e:
        print(f"{ICONS['error']} OS error during move: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not move {src}: {str(e)}")
        return False

def search_files(directory, name=None, ext=None, keyword=None):
    """Search files with comprehensive error handling"""
    valid, error = validate_path(directory, should_exist=True, path_type='dir')
    if not valid:
        print(error)
        return False

    try:
        if not os.access(directory, os.R_OK):
            print(f"{ICONS['error']} Permission denied - cannot read directory: {directory}")
            return False
        
        loading_effect("Searching files")
        found_files = False
        search_count = 0
        
        for root, _, files in os.walk(directory):
            # Check if we can read this directory
            if not os.access(root, os.R_OK):
                print(f"{ICONS['warning']} Skipped (permission denied): {root}")
                continue
            
            for file in files:
                try:
                    if name and name.lower() not in file.lower():
                        continue
                    if ext and not file.lower().endswith(ext.lower()):
                        continue
                    if keyword:
                        try:
                            file_path = os.path.join(root, file)
                            if not os.access(file_path, os.R_OK):
                                continue
                            with open(file_path, "r", errors="ignore", encoding="utf-8") as f:
                                if keyword.lower() not in f.read().lower():
                                    continue
                        except (PermissionError, IOError):
                            continue
                    
                    file_path = os.path.join(root, file)
                    print(f"{ICONS['search']} {file_path}")
                    found_files = True
                    search_count += 1
                except Exception:
                    continue
        
        if not found_files:
            print(f"{ICONS['info']} No matching files found")
        else:
            print(f"{ICONS['info']} Found {search_count} matching file(s)")
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot access directory")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} Directory not found: {directory}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Error during search: {str(e)}")
        return False

def compress_files(src, dst):
    """Compress files with comprehensive error handling"""
    valid_src, error_src = validate_path(src, should_exist=True)
    if not valid_src:
        print(error_src)
        return False
    
    if not dst or not isinstance(dst, str):
        print(f"{ICONS['error']} Destination path cannot be empty")
        return False
    
    dst = dst.strip()
    if not dst.lower().endswith('.zip'):
        print(f"{ICONS['warning']} Adding .zip extension to destination")
        dst += '.zip'
    
    try:
        # Check source readability
        if not os.access(src, os.R_OK):
            print(f"{ICONS['error']} Permission denied - cannot read source")
            return False
        
        # Create parent directory and check write permission
        dst_parent = Path(dst).parent
        if not dst_parent.exists():
            dst_parent.mkdir(parents=True, exist_ok=True)
        
        if not os.access(dst_parent, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot write to destination directory")
            return False
        
        # Check if destination already exists
        if os.path.exists(dst):
            print(f"{ICONS['warning']} Archive already exists, will be overwritten: {dst}")
        
        loading_effect("Compressing")
        file_count = 0
        
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(src):
                for root, _, files in os.walk(src):
                    if not os.access(root, os.R_OK):
                        print(f"{ICONS['warning']} Skipped (no permission): {root}")
                        continue
                    for file in files:
                        try:
                            fpath = os.path.join(root, file)
                            if os.access(fpath, os.R_OK):
                                zf.write(fpath, os.path.relpath(fpath, src))
                                file_count += 1
                        except (PermissionError, IOError):
                            continue
                
                if file_count == 0:
                    print(f"{ICONS['warning']} Source directory is empty or all files are inaccessible")
                    return False
            else:
                zf.write(src, os.path.basename(src))
                file_count = 1
        
        print(f"{ICONS['success']} {ICONS['compress']} Compressed {file_count} file(s): {src} → {dst}")
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot create archive")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} Source not found: {src}")
        return False
    except zipfile.BadZipFile:
        print(f"{ICONS['error']} Failed to create valid ZIP file")
        return False
    except OSError as e:
        print(f"{ICONS['error']} OS error during compression: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not compress {src}: {str(e)}")
        return False

def extract_zip(src, dst):
    """Extract ZIP file with comprehensive error handling"""
    valid_src, error_src = validate_path(src, should_exist=True, path_type='file')
    if not valid_src:
        print(error_src)
        return False
    
    if not src.lower().endswith('.zip'):
        print(f"{ICONS['error']} Source file is not a ZIP archive: {src}")
        return False
    
    if not dst or not isinstance(dst, str):
        print(f"{ICONS['error']} Destination path cannot be empty")
        return False
    
    dst = dst.strip()

    try:
        # Check source readability
        if not os.access(src, os.R_OK):
            print(f"{ICONS['error']} Permission denied - cannot read ZIP file")
            return False
        
        # Create destination directory
        dst_path = Path(dst)
        if not dst_path.exists():
            dst_path.mkdir(parents=True, exist_ok=True)
        
        # Check write permission on destination
        if not os.access(dst, os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot write to destination")
            return False
        
        loading_effect("Extracting")
        
        # Validate and extract ZIP file
        try:
            with zipfile.ZipFile(src, "r") as zf:
                # Test ZIP integrity
                test_result = zf.testzip()
                if test_result is not None:
                    print(f"{ICONS['error']} ZIP file is corrupted, first bad file: {test_result}")
                    return False
                
                # Extract files
                file_count = len(zf.namelist())
                zf.extractall(dst)
                
        except zipfile.BadZipFile:
            print(f"{ICONS['error']} Invalid or corrupted ZIP file: {src}")
            return False
        except zipfile.LargeZipFile:
            print(f"{ICONS['error']} ZIP file is too large")
            return False
        
        print(f"{ICONS['success']} {ICONS['extract']} Extracted {file_count} file(s): {src} → {dst}")
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot extract archive")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} ZIP file not found: {src}")
        return False
    except IsADirectoryError:
        print(f"{ICONS['error']} Source is a directory, not a ZIP file")
        return False
    except OSError as e:
        print(f"{ICONS['error']} OS error during extraction: {str(e)}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not extract {src}: {str(e)}")
        return False

def organize_files(folder, dry_run=False, compress=False, compress_path=None):
    """Organize files with comprehensive error handling"""
    if not folder or not isinstance(folder, str):
        print(f"{ICONS['error']} Folder path cannot be empty")
        return False
    
    folder = folder.strip()
    folder_path = Path(folder)
    
    try:
        if not folder_path.exists():
            print(f"{ICONS['error']} Folder does not exist: {folder}")
            return False
        
        if not folder_path.is_dir():
            print(f"{ICONS['error']} Path is not a directory: {folder}")
            return False
        
        if not os.access(folder, os.R_OK | os.W_OK):
            print(f"{ICONS['error']} Permission denied - cannot access folder")
            return False
        
        processed = []
        print(f"\n{ICONS['organize']} Organizing files by type...\n")
        
        for file in folder_path.iterdir():
            try:
                if file.is_file():
                    if not os.access(file, os.R_OK | os.W_OK):
                        print(f"{ICONS['warning']} Skipped (no permission): {file.name}")
                        continue
                    
                    ext = file.suffix.lower()
                    category = EXTENSION_FOLDERS.get(ext, "Misc")
                    target_dir = folder_path / category
                    
                    try:
                        target_dir.mkdir(exist_ok=True)
                    except PermissionError:
                        print(f"{ICONS['error']} Cannot create directory: {category}")
                        continue

                    new_path = target_dir / file.name
                    if dry_run:
                        print(f"{ICONS['info']} [Dry-run] {file.name} → {category}/")
                    else:
                        try:
                            shutil.move(str(file), str(new_path))
                            processed.append(new_path)
                            print(f"{ICONS['success']} {ICONS['file']} {file.name} → {category}/")
                            check_suggest_compress(new_path)
                        except (PermissionError, shutil.Error) as e:
                            print(f"{ICONS['error']} Could not move {file.name}: {str(e)}")
                            continue
            except (PermissionError, OSError) as e:
                print(f"{ICONS['warning']} Skipped: {str(e)}")
                continue

        if compress and processed:
            zip_dir = Path(compress_path) if compress_path else folder_path / "Compressed"
            try:
                zip_dir.mkdir(exist_ok=True)
                zip_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                zip_path = zip_dir / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file in processed:
                        zf.write(file, file.name)
                print(f"\n{ICONS['success']} {ICONS['compress']} Compressed {len(processed)} files into {zip_path}")
            except PermissionError:
                print(f"{ICONS['error']} Permission denied - cannot create archive")
            except Exception as e:
                print(f"{ICONS['error']} Error creating archive: {str(e)}")
        
        return True
    except PermissionError:
        print(f"{ICONS['error']} Permission denied - cannot access folder")
        return False
    except FileNotFoundError:
        print(f"{ICONS['error']} Folder not found: {folder}")
        return False
    except Exception as e:
        print(f"{ICONS['error']} Could not organize folder: {str(e)}")
        return False
    if not folder.exists():
        print(f"{ICONS['error']} Folder does not exist.")
        return False

    try:
        processed = []
        print(f"\n{ICONS['organize']} Organizing files by type...\n")
        
        for file in folder.iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                category = EXTENSION_FOLDERS.get(ext, "Misc")
                target_dir = folder / category
                target_dir.mkdir(exist_ok=True)

                new_path = target_dir / file.name
                if dry_run:
                    print(f"{ICONS['info']} [Dry-run] {file.name} → {category}/")
                else:
                    shutil.move(str(file), str(new_path))
                    processed.append(new_path)
                    print(f"{ICONS['success']} {ICONS['file']} {file.name} → {category}/")
                    check_suggest_compress(new_path)

        if compress and processed:
            zip_dir = Path(compress_path) if compress_path else folder / "Compressed"
            zip_dir.mkdir(exist_ok=True)
            zip_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = zip_dir / zip_name
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in processed:
                    zf.write(file, file.name)
            print(f"\n{ICONS['success']} {ICONS['compress']} Compressed {len(processed)} files into {zip_path}")
        
        return True
    except Exception as e:
        print(f"{ICONS['error']} Could not organize folder: {e}")
        return False

# ------------------- STORAGE ANALYSIS ------------------- #
def storage_analysis():
    print(f"\n{ICONS['storage']} === Storage Analysis ===\n")
    system = platform.system()

    drives = []
    if system == "Windows":
        from string import ascii_uppercase
        drives = [f"{d}:/" for d in ascii_uppercase if os.path.exists(f"{d}:/")]
    else:
        drives = ["/"]

    print(f"{ICONS['info']} Scanning drives...\n")
    for d in drives:
        try:
            usage = shutil.disk_usage(d)
            total = usage.total // (1024**3)
            used = usage.used // (1024**3)
            free = usage.free // (1024**3)
            usage_percent = (used / total * 100) if total > 0 else 0
            bar = "█" * int(usage_percent / 5) + "░" * (20 - int(usage_percent / 5))
            print(f"{ICONS['folder']} Drive {d:<4} │ [{bar}] {usage_percent:>5.1f}% │ {used:>4}/{total:>4} GB")
        except Exception as e:
            print(f"{ICONS['error']} Could not access {d}: {e}")

    temp_dir = tempfile.gettempdir()
    print(f"\n{ICONS['temp']} Temporary files location: {temp_dir}")
    choice = input(f"{ICONS['info']} Delete all temporary files? (yes/no): ").strip().lower()
    if choice == "yes":
        loading_effect("Cleaning temp files")
        try:
            deleted_count = 0
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                        deleted_count += 1
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                    except:
                        pass
            print(f"{ICONS['success']} {ICONS['temp']} Cleaned {deleted_count} temporary items")
        except Exception as e:
            print(f"{ICONS['error']} Could not delete temp files: {e}")
    else:
        print(f"{ICONS['info']} Temp files not deleted.")

# ------------------- SUGGEST COMPRESSION ------------------- #
def check_suggest_compress(path, threshold_mb=50):
    """Suggest compressing file if larger than threshold"""
    try:
        if os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if size_mb > threshold_mb:
                print(f"{ICONS['warning']} {ICONS['compress']} File {path} is {size_mb:.1f} MB. Consider compressing it!")
    except Exception:
        pass

# ------------------- INTERACTIVE MENU ------------------- #
def menu_mode():
    while True:
        print("\n" + "=" * 60)
        print(f"{ICONS['file']} File Operations Menu")
        print("=" * 60)
        print(f"{ICONS['create']}  1) Create File")
        print(f"{ICONS['read']}  2) Read File")
        print(f"{ICONS['write']}  3) Write File")
        print(f"{ICONS['append']}  4) Append File")
        print(f"{ICONS['rename']}  5) Rename File/Folder")
        print(f"{ICONS['delete']}  6) Delete File/Folder")
        print(f"{ICONS['copy']}  7) Copy File/Folder")
        print(f"{ICONS['move']}  8) Move File/Folder")
        print(f"{ICONS['search']}  9) Search Files")
        print(f"{ICONS['compress']} 10) Compress")
        print(f"{ICONS['extract']} 11) Extract")
        print(f"{ICONS['organize']} 12) Organize Folder")
        print(f"{ICONS['storage']} 13) Storage Analysis & Temp Cleanup")
        print(f"🚪 0) Exit")
        print("=" * 60)
        
        try:
            choice = input(f"{ICONS['info']} Choose option: ").strip()

            if choice == "1":
                path = input(f"{ICONS['create']} Enter file path: ").strip()
                if path:
                    create_file(path)
                else:
                    print(f"{ICONS['error']} File path cannot be empty")
            elif choice == "2":
                path = input(f"{ICONS['read']} Enter file path: ").strip()
                if path:
                    read_file(path)
                else:
                    print(f"{ICONS['error']} File path cannot be empty")
            elif choice == "3":
                path = input(f"{ICONS['write']} Enter file path: ").strip()
                if path:
                    text = input(f"{ICONS['write']} Enter text: ")
                    write_file(path, text, append=False)
                else:
                    print(f"{ICONS['error']} File path cannot be empty")
            elif choice == "4":
                path = input(f"{ICONS['append']} Enter file path: ").strip()
                if path:
                    text = input(f"{ICONS['append']} Enter text: ")
                    write_file(path, text, append=True)
                else:
                    print(f"{ICONS['error']} File path cannot be empty")
            elif choice == "5":
                src = input(f"{ICONS['rename']} Enter source path: ").strip()
                dst = input(f"{ICONS['rename']} Enter destination path: ").strip()
                if src and dst:
                    rename_item(src, dst)
                else:
                    print(f"{ICONS['error']} Both source and destination paths are required")
            elif choice == "6":
                path = input(f"{ICONS['delete']} Enter path: ").strip()
                if path:
                    if input(f"{ICONS['warning']} Are you sure? (yes/no): ").lower() == 'yes':
                        delete_item(path)
                    else:
                        print(f"{ICONS['info']} Delete cancelled")
                else:
                    print(f"{ICONS['error']} Path cannot be empty")
            elif choice == "7":
                src = input(f"{ICONS['copy']} Enter source path: ").strip()
                dst = input(f"{ICONS['copy']} Enter destination path: ").strip()
                if src and dst:
                    copy_item(src, dst)
                else:
                    print(f"{ICONS['error']} Both source and destination paths are required")
            elif choice == "8":
                src = input(f"{ICONS['move']} Enter source path: ").strip()
                dst = input(f"{ICONS['move']} Enter destination path: ").strip()
                if src and dst:
                    move_item(src, dst)
                else:
                    print(f"{ICONS['error']} Both source and destination paths are required")
            elif choice == "9":
                directory = input(f"{ICONS['search']} Enter directory: ").strip()
                if directory:
                    search_files(
                        directory,
                        name=input(f"{ICONS['search']} Name (optional): ").strip() or None,
                        ext=input(f"{ICONS['search']} Extension (optional, e.g. .txt): ").strip() or None,
                        keyword=input(f"{ICONS['search']} Keyword (optional): ").strip() or None
                    )
                else:
                    print(f"{ICONS['error']} Directory path cannot be empty")
            elif choice == "10":
                src = input(f"{ICONS['compress']} Enter source path: ").strip()
                dst = input(f"{ICONS['compress']} Enter destination .zip path: ").strip()
                if src and dst:
                    if not dst.lower().endswith('.zip'):
                        dst += '.zip'
                    compress_files(src, dst)
                else:
                    print(f"{ICONS['error']} Both source and destination paths are required")
            elif choice == "11":
                src = input(f"{ICONS['extract']} Enter .zip path: ").strip()
                dst = input(f"{ICONS['extract']} Enter destination folder: ").strip()
                if src and dst:
                    extract_zip(src, dst)
                else:
                    print(f"{ICONS['error']} Both source and destination paths are required")
            elif choice == "12":
                path = input(f"{ICONS['organize']} Enter folder path: ").strip()
                if path:
                    organize_files(path)
                else:
                    print(f"{ICONS['error']} Folder path cannot be empty")
            elif choice == "13":
                storage_analysis()
            elif choice == "0":
                print(f"\n{ICONS['success']} Goodbye 👋\n")
                break
            else:
                print(f"{ICONS['error']} Invalid choice.")
                
        except KeyboardInterrupt:
            print(f"\n{ICONS['info']} Operation cancelled")
            continue
        except Exception as e:
            print(f"{ICONS['error']} An error occurred: {str(e)}")
            continue
        
        input(f"\n{ICONS['info']} Press Enter to continue...")

# ------------------- CLI ------------------- #
def main():
    parser = argparse.ArgumentParser(description="File Operations CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # menu
    subparsers.add_parser("menu", help="Run interactive menu")

    # storage
    subparsers.add_parser("storage", help="Run storage analysis and temp cleanup")

    # compress
    sp_compress = subparsers.add_parser("compress", help="Compress files/folders")
    sp_compress.add_argument("src")
    sp_compress.add_argument("dst")

    # extract
    sp_extract = subparsers.add_parser("extract", help="Extract zip file")
    sp_extract.add_argument("src")
    sp_extract.add_argument("dst")

    args = parser.parse_args()

    if args.command == "menu":
        menu_mode()
    elif args.command == "storage":
        storage_analysis()
    elif args.command == "compress":
        compress_files(args.src, args.dst)
    elif args.command == "extract":
        extract_zip(args.src, args.dst)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{ICONS['info']} Cancelled by user.")
        sys.exit(1)