# Pure Python Back SEO Agencies

![Screenshot from 2025-03-16 13-24-59](https://github.com/user-attachments/assets/7f52445f-2ff2-4bf5-9b07-7fcbf9a0dd29)

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Introduction

Pure Python Back SEO Agencies is a comprehensive SEO analysis and reporting tool designed to help SEO agencies manage and create professional reports for their clients. Built entirely in Python, this tool provides powerful features for analyzing search engine results, auditing websites, and generating detailed local ranking reports.

## Features

### 🔍 **Google Results Inspector**
- Analyze search results from a single page
- Extract keywords, content length, headers, and readability metrics
- Identify Schema markup and structured data
- Generate detailed competitor analysis reports

### 🚀 **Fast Website Auditing**
- Audit up to 1000+ pages in under 5 minutes
- Analyze sitemaps for comprehensive site coverage
- Identify technical SEO issues and optimization opportunities
- Generate actionable recommendations

### 📍 **Local Rank Grid Map Reporting**
- Track local search rankings across different locations
- Visualize ranking performance on interactive maps
- Monitor competitor positions in local search
- Generate geo-targeted ranking reports

## Prerequisites

Before you can install and run this tool, ensure you have the following installed:

- **Python 3.12 or later** (Python 3.13 recommended)
- **UV** (Fast Python package installer) - [Install UV](https://github.com/astral-sh/uv)
- **Git** for cloning the repository

## Installation

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/awcook97/Pure-Python-Back-SEO.git
   cd Pure-Python-Back-SEO
   ```

2. **Set up virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install firefox
   ```

### Alternative Installation (using pip)

If you prefer using pip instead of uv:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install firefox
```

## Usage

### Running the Main Application

Start the GUI application:
```bash
python BackSEOAgencies.py
```

Or use the main entry point:
```bash
python __main__.py
```

### Running the Flask Web Interface

For web-based access:
```bash
python FlaskApp.py
```

Then open your browser and navigate to `http://localhost:5000`

## Configuration

The application can be configured through the `BackSEOSettings.py` file. Key settings include:

- **Performance settings**: CPU cores, thread count, FPS limits
- **Display settings**: Window size, theme preferences
- **Report settings**: Output formats, template selection

## Testing

Run the test suite to ensure everything is working correctly:

```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Troubleshooting

### Common Issues

**Issue: Playwright browser not found**
```bash
# Solution: Reinstall Playwright browsers
playwright install firefox
```

**Issue: Module not found errors**
```bash
# Solution: Ensure you're in the virtual environment and dependencies are installed
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Issue: Permission denied when running on Linux/Mac**
```bash
# Solution: Make the script executable
chmod +x BackSEOAgencies.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- How to submit bug reports
- How to propose new features
- Development setup and workflow
- Code style guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [DearPyGUI](https://github.com/hoffstadt/DearPyGui) for the user interface
- Powered by [Playwright](https://playwright.dev/) for web automation
- SEO analysis tools built on top of industry-standard libraries

## Support

If you find this tool useful, please:
- ⭐ Star this repository
- 🐛 Report bugs via [GitHub Issues](https://github.com/awcook97/Pure-Python-Back-SEO/issues)
- 💡 Share your feedback and suggestions
- 📢 Spread the word about this tool

---

**Ready to improve your SEO reporting?** Clone this repo, set it up, and start creating professional reports for your clients today!
