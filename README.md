# File Operations CLI Tool

A comprehensive command-line tool for file and folder operations, including create, read, write, append, rename, delete, copy, move, search, compress, extract, organize files by type, storage analysis, and temporary file cleanup. Features interactive menu mode, dry-run support, loading effects, and works across drives.

## Installation

1. Ensure Python 3 is installed on your system.
2. Download or clone the repository containing `file.py`.
3. No additional dependencies are required beyond the Python standard library.

## Usage

### Interactive Menu Mode
Run the tool in interactive mode for a user-friendly menu:

```bash
python file.py menu
```

Available menu options:
- Create File
- Read File
- Write File
- Append File
- Rename File/Folder
- Delete File/Folder
- Copy File/Folder
- Move File/Folder
- Search Files (by name, extension, or keyword)
- Compress Files/Folders
- Extract ZIP Files
- Organize Folder (by file type)
- Storage Analysis & Temp Cleanup

### Command-Line Interface
Use specific commands for direct operations:

- **Storage Analysis**: `python file.py storage`
- **Compress**: `python file.py compress <source> <destination.zip>`
- **Extract**: `python file.py extract <source.zip> <destination>`

### Features
- Comprehensive error handling and permission checks
- Loading effects for operations
- Compression suggestions for large files
- Dry-run support for organization
- Cross-platform compatibility (Windows, Linux, macOS)
- Works across multiple drives

## Contributing

Guidelines for contributing to the project.

## License

Information about the project's license.
