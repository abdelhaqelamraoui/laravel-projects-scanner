# Laravel Projects Scanner

A beautiful, Material Design-inspired desktop application for scanning and managing Laravel projects on your local machine. Built with Python and Tkinter, featuring a modern UI with Laravel's signature red color scheme.

![Laravel Projects Scanner](https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)

## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

## ✨ Features

- **🔍 Smart Project Detection**: Automatically scans directories to find Laravel projects by detecting `artisan` file and `laravel/framework` dependency
- **📁 Persistent Storage**: Saves scanned project paths to a file for quick access on next launch
- **✅ Project Validation**: On startup, automatically validates and removes deleted projects from the list
- **📦 Vendor Directory Management**: 
  - Visual indicators showing which projects have `vendor/` directories
  - Bulk removal of vendor packages from selected projects
- **🔗 Quick Actions**:
  - Open projects directly in VSCode with one click
  - Open project folders in file explorer
- **🎨 Material Design UI**: Beautiful, modern interface with Laravel's color scheme
- **💾 Auto-save**: Remembers the last scanned folder path
- **📊 Project List**: Scrollable list with all your Laravel projects

## 🖼️ Screenshots

The application features a clean, Material Design-inspired interface with:
- Laravel red header bar
- Card-based layout for better organization
- Color-coded vendor directory indicators
- Compact, efficient use of space

## 🚀 Installation

### Prerequisites

- Python 3.6 or higher
- Tkinter (usually included with Python)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/abdelhaqelamraoui/laravel-projects-scanner.git
cd laravel-projects-scanner
```

2. Run the application:
```bash
python main.py
```

No additional dependencies required! The application uses only Python standard library modules.

## 📖 Usage

### Scanning for Projects

1. **Launch the application**: Run `python main.py`
2. **Select a folder**: Click "Browse" to choose the directory you want to scan
3. **Scan**: Click "Scan Projects" to find all Laravel projects in the selected directory
4. **View results**: All found Laravel projects will be displayed in the list

### Managing Projects

- **Open in VSCode**: Click the "VSCode" button next to any project
- **Open folder**: Double-click on a project path to open it in your file explorer
- **Remove vendor packages**: 
  - Check the boxes next to projects with vendor directories
  - Click "Remove Vendor Packages" to delete `vendor/` folders from selected projects

### Project Persistence

- Projects are automatically saved to `laravel_projects.txt`
- The last scanned folder is saved to `scanned_folder.txt`
- On startup, the app validates all saved projects and removes any that no longer exist

## 📁 Project Structure

```
laravel_scanner/
├── main.py              # Application entry point
├── gui.py               # Main GUI application with Material Design styling
├── scanner.py           # Core scanning logic for detecting Laravel projects
├── utils.py             # Utility functions (file operations, VSCode integration)
├── laravel_projects.txt # Stored project paths (auto-generated)
├── scanned_folder.txt   # Last scanned folder path (auto-generated)
└── README.md           # This file
```

## 🔧 How It Works

### Project Detection

The scanner identifies Laravel projects by checking for:
1. Presence of `artisan` file (Laravel's command-line tool)
2. Presence of `composer.json` file
3. `laravel/framework` dependency in `composer.json`

### File Storage

- **laravel_projects.txt**: Stores all discovered Laravel project paths with metadata
- **scanned_folder.txt**: Remembers the last directory you scanned for convenience

### Vendor Directory Detection

The app checks each project for the presence of a `vendor/` directory and displays:
- ✓ (green) if vendor directory exists
- ✗ (gray) if vendor directory doesn't exist

## 🤝 Contributing

We welcome contributions! This project is open for improvements and new features. Here's how you can help:

### Ways to Contribute

- 🐛 **Report bugs**: Found an issue? Open an issue on GitHub
- 💡 **Suggest features**: Have an idea? We'd love to hear it!
- 🔧 **Submit pull requests**: Fix bugs or add features
- 📝 **Improve documentation**: Help make the README better
- 🎨 **UI/UX improvements**: Enhance the Material Design interface
- ⚡ **Performance optimizations**: Make the scanner faster
- 🌐 **Multi-language support**: Add translations

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Improvement

- [ ] Add support for scanning multiple directories
- [ ] Implement project filtering and search
- [ ] Add project statistics (Laravel version, dependencies, etc.)
- [ ] Export project list to different formats (CSV, JSON)
- [ ] Add dark mode support
- [ ] Implement project grouping/folders
- [ ] Add keyboard shortcuts
- [ ] Support for other IDEs (PhpStorm, Sublime Text, etc.)
- [ ] Add project health checks
- [ ] Implement batch operations (composer install, npm install, etc.)

## 👤 Author

**Abdelhaq El Amraoui**

- GitHub: [@abdelhaqelamraoui](https://github.com/abdelhaqelamraoui)
- Project Repository: [laravel-projects-scanner](https://github.com/abdelhaqelamraoui/laravel-projects-scanner)

Made with ❤️ by [Abdelhaq El Amraoui](https://github.com/abdelhaqelamraoui/laravel-projects-scanner)

## 📄 License

This project is open source and available for use, modification, and distribution. Feel free to use it in your projects!

## 🙏 Acknowledgments

- Built with [Laravel](https://laravel.com) in mind
- UI inspired by [Material Design](https://material.io/design)
- Thanks to all contributors who help improve this project!

---

⭐ If you find this project useful, please consider giving it a star on GitHub!

