#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 11:35:00 (ywatanabe)"

"""
File utilities for SciTex
"""

import os
import shutil
import difflib
from typing import Optional, Tuple, Dict

from config import DIFF_COLORS

def load_tex(file_path: str) -> str:
    """
    Load content from a TeX file.
    
    Args:
        file_path: Path to the TeX file
        
    Returns:
        The content of the file as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there's an error reading the file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")

def save_tex(content: str, file_path: str) -> None:
    """
    Save content to a TeX file.
    
    Args:
        content: The content to save
        file_path: Path where the file should be saved
        
    Raises:
        IOError: If there's an error writing to the file
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except IOError as e:
        raise IOError(f"Error writing to file {file_path}: {str(e)}")

def back_up(file_path: str) -> str:
    """
    Create a backup of a file in a .old directory.
    
    Args:
        file_path: Path to the file to back up
        
    Returns:
        Path to the backup file
        
    Raises:
        FileNotFoundError: If the source file does not exist
        IOError: If there's an error creating the backup
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Create backup directory
        dir_path, file_name = os.path.split(file_path)
        backup_dir = os.path.join(dir_path, ".old")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup file path
        backup_path = os.path.join(backup_dir, file_name)
        
        # Copy the file
        shutil.copy2(file_path, backup_path)
        print(f"Backed up: {file_path} -> {backup_path}")
        
        return backup_path
    except IOError as e:
        raise IOError(f"Error creating backup of {file_path}: {str(e)}")

def show_diff(a: str, b: str, for_tex: bool = False) -> str:
    """
    Generate a colored diff between two strings.
    
    Args:
        a: First string (original)
        b: Second string (modified)
        for_tex: Whether to use TeX-compatible color codes
        
    Returns:
        A string with colored differences
    """
    output = []
    matcher = difflib.SequenceMatcher(None, a, b)
    
    # Select color set based on output format
    colors = DIFF_COLORS["tex"] if for_tex else DIFF_COLORS["bash"]
    
    # Generate diff with color markup
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            output.append(a[a0:a1])
        elif opcode == 'insert':
            output.append(f'{colors["start_green"]}{b[b0:b1]}{colors["end_green"]}')
        elif opcode == 'delete':
            output.append(f'{colors["start_red"]}{a[a0:a1]}{colors["end_red"]}')
        elif opcode == 'replace':
            output.append(f'{colors["start_green"]}{b[b0:b1]}{colors["end_green"]}')
            output.append(f'{colors["start_red"]}{a[a0:a1]}{colors["end_red"]}')
            
    return ''.join(output)

def ensure_dir(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
        
    Raises:
        IOError: If there's an error creating the directory
    """
    try:
        os.makedirs(directory, exist_ok=True)
    except IOError as e:
        raise IOError(f"Error creating directory {directory}: {str(e)}")
        
def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file extension (without the dot)
    """
    _, extension = os.path.splitext(file_path)
    return extension[1:] if extension.startswith('.') else extension