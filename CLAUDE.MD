# CLAUDE.MD

This file contains instructions and context for Claude Code to help understand and work with this project.

## Project Overview

**Project Name:** 図面拾いツール (Drawing Extraction Tool)

This is a Python-based tool for automatically extracting dimensions, areas, and quantities from architectural drawings. It supports PDF files, images, and manual input, with OCR capabilities for text recognition.

**Primary Language:** Python
**Domain:** Construction/Architecture - Quantity Takeoff (積算)

## Development Guidelines

### Code Style
- Follow language-specific best practices and conventions
- Keep code clean, readable, and maintainable
- Use meaningful variable and function names
- Add comments only where the logic isn't self-evident

### Git Workflow
- Work on feature branches (preferably starting with `claude/` for AI-assisted development)
- Write clear, descriptive commit messages
- Commit message format: Start with a verb (Add, Update, Fix, Remove, etc.) followed by a concise description
- Keep commits focused on single logical changes

### Testing
- Write tests for new features and bug fixes
- Run existing tests before committing changes
- Ensure all tests pass before pushing

## Project Structure

```
fluffy/
├── README.md                    # Project documentation (Japanese)
├── CLAUDE.MD                    # This file - instructions for Claude Code
├── requirements.txt             # Python dependencies
├── config.json                  # Configuration file for the tool
├── drawing_extractor.py         # Main drawing extraction tool
├── image_extractor.py           # Image processing and OCR extension
├── example_basic.py             # Usage examples and demonstrations
├── .gitignore                   # Git ignore file
└── .git/                        # Git repository
```

## Key Components

### drawing_extractor.py
- Core drawing extraction functionality
- Measurement data classes and enums
- Text-based dimension extraction using regex
- PDF processing with PyPDF2/pdfplumber
- Area, perimeter, and count calculations
- JSON and CSV export functionality

### image_extractor.py
- Image-based drawing processing
- OCR capabilities (pytesseract, easyocr)
- Line detection using OpenCV
- Visual detection result overlay
- Extends DrawingExtractor base class

### example_basic.py
- Three comprehensive usage examples
- Manual input example
- Text extraction example
- Construction quantity takeoff example

### config.json
- Default scale settings
- Unit definitions
- Extraction regex patterns
- Output format configurations
- Standard dimensions for common elements

## Notes for Claude Code

- Always read files before modifying them
- Prefer editing existing files over creating new ones
- Avoid over-engineering - keep solutions simple and focused
- Only make changes that are directly requested or clearly necessary
- Ask questions when requirements are unclear
- Use the TodoWrite tool to track multi-step tasks

## Environment

- Repository: fluffy
- Development branch pattern: `claude/*`

## Dependencies

### Required (Basic)
- PyPDF2 or pdfplumber: PDF processing

### Optional (Full Features)
- Pillow: Image file handling
- opencv-python: Line detection and image processing
- pytesseract or easyocr: OCR for text extraction from images
- numpy, pandas: Data processing

## Usage Patterns

### Basic Workflow
1. Initialize extractor with scale (e.g., 1/100 = 0.01)
2. Extract measurements from text/PDF/image
3. Add manual calculations if needed
4. Export results to JSON/CSV

### Scale Settings
- 1/100 scale: `scale=0.01`
- 1/50 scale: `scale=0.02`
- 1/200 scale: `scale=0.005`

## Architecture Decisions

### Object-Oriented Design
- Base class `DrawingExtractor` for core functionality
- Extended classes `PDFDrawingExtractor` and `ImageDrawingExtractor`
- Dataclass `Measurement` for type-safe measurement storage
- Enum `MeasurementType` for measurement categorization

### Measurement Types
1. LENGTH: Linear measurements in mm
2. AREA: Surface area in m²
3. COUNT: Quantity counts (integer values)
4. PERIMETER: Perimeter calculations in mm

### Text Extraction Patterns
Uses regex to match common Japanese construction notation:
- Lengths: "3,000mm", "3.5m"
- Areas: "15.5㎡", "15.5m²"
- Mixed metric units with automatic conversion

## Common Use Cases

1. **Residential Floor Plans**: Room areas, wall lengths, equipment counts
2. **Construction Estimates**: Material quantity calculations
3. **Renovation Projects**: Existing building measurements

## Testing

Run the example script to verify functionality:
```bash
python example_basic.py
```

This will generate sample JSON and CSV outputs for verification.
