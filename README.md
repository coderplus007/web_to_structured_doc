# Web to Structured Doc

An enhanced web documentation tool that converts website menu structures into hierarchical document chapters for better organized documentation exports.

## 🌟 Features

- **Menu Structure Detection**: Automatically identifies navigation menus on websites
- **Hierarchical Chapter Conversion**: Transforms website navigation into properly nested document chapters
- **Multiple Output Formats**: Exports to PDF, HTML, Markdown, DOCX with preserved structure
- **Customizable Structure Mapping**: Configure how menu items map to document sections
- **Smart Content Organization**: Groups related content based on site hierarchy
- **Table of Contents Generation**: Creates ToC based on the identified structure
- **Cross-Reference Preservation**: Maintains internal linking between sections
- **Flexible Configuration**: Customize depth, selectors, and recognition patterns

## 🔍 How It Works

The tool enhances the standard web crawling process with structure detection:

1. **Initial Analysis**: Examines the website to detect navigation and menu patterns
2. **Structure Mapping**: Creates a hierarchical map of the site based on navigation elements
3. **Content Crawling**: Retrieves content while preserving its position in the hierarchy
4. **Structural Processing**: Orders and nests content according to the site structure
5. **Formatted Output**: Generates documents with proper chapter hierarchies

## 📋 Installation

```bash
# Clone the repository
git clone https://github.com/coderplus007/web_to_structured_doc.git
cd web_to_structured_doc

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Basic Usage

```bash
python web_to_structured_doc.py --url https://docs.example.com/
```

### Specifying Structure Options

```bash
python web_to_structured_doc.py --url https://docs.example.com/ \
  --menu-selector "nav.main-navigation" \
  --structure-depth 3 \
  --chapter-numbering
```

### Customizing Output

```bash
python web_to_structured_doc.py --url https://docs.example.com/ \
  --format pdf \
  --output documentation.pdf \
  --toc
```

## 📝 Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | URL to start crawling from | (Required) |
| `--output` | Output file path | `output.[format]` |
| `--format` | Output format: pdf, html, md, docx | `pdf` |
| `--menu-selector` | CSS selector for the navigation menu | Auto-detect |
| `--structure-depth` | Maximum depth of chapters to extract | No limit |
| `--chapter-numbering` | Add automatic chapter numbers | False |
| `--structure-only` | Only extract structure without full content | False |
| `--max-pages` | Maximum number of pages to process | 250 |
| `--delay` | Delay between requests in seconds | 1 |
| `--contains` | Only include pages containing keywords | None |
| `--not-contains` | Exclude pages containing keywords | None |
| `--toc` | Generate table of contents | False |
| `--interactive` | Interactive mode for structure selection | False |

## 🔎 Menu Structure Detection

The tool uses several methods to identify navigation structures:

1. **Common Selectors**: Looks for typical navigation elements like `<nav>`, `.navigation`, `.menu`
2. **Hierarchical Analysis**: Identifies nested list structures that indicate menus
3. **Link Density**: Detects areas with high concentration of internal links
4. **Header Proximity**: Recognizes navigation elements near site headers
5. **Semantic Elements**: Utilizes HTML5 semantic markup when available

You can override automatic detection with the `--menu-selector` parameter.

## 📑 Output Format Details

### PDF

- Creates structured PDF with proper chapter hierarchy
- Supports nested bookmarks for navigation
- Automatic chapter numbering (optional)
- Table of contents with page numbers

### HTML

- Single HTML file with preserved structure
- Nested section elements with appropriate heading levels
- CSS styling for hierarchical navigation
- Clickable table of contents

### Markdown

- Clean, structured Markdown with heading levels reflecting hierarchy
- Section links for cross-referencing
- Table of contents with proper nesting
- Compatible with most Markdown renderers

### DOCX (Microsoft Word)

- Proper document outline with heading styles
- Automatic generation of Word's native table of contents
- Document sections with appropriate hierarchy
- Page breaks between major sections

## 🧩 Components

The project consists of several modular components:

- **Structure Detector**: Identifies navigation and menu structures
- **Content Crawler**: Retrieves page content while tracking structural position
- **Hierarchy Builder**: Constructs the document tree from discovered content
- **Format Generators**: Output generators for different document formats
- **Configuration Manager**: Handles user preferences and settings

## 🛠️ Development

### Project Structure

```
web_to_structured_doc/
├── web_to_structured_doc.py      # Main script
├── lib/
│   ├── structure_detector.py     # Menu structure detection
│   ├── content_crawler.py        # Content retrieval
│   ├── hierarchy_builder.py      # Document hierarchy construction
│   ├── format_generators/        # Output format generators
│   │   ├── pdf_generator.py
│   │   ├── html_generator.py
│   │   ├── markdown_generator.py
│   │   └── docx_generator.py
│   └── utils.py                  # Utility functions
├── config/
│   └── default_selectors.json    # Default CSS selectors for navigation
└── tests/                        # Test suite
```

### Adding New Features

The modular architecture makes it easy to extend the tool. Focus areas for contribution:

- Support for more document formats
- Enhanced menu detection algorithms
- Support for single-page applications
- Improved content extraction for complex layouts

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [web_to_doc](https://github.com/coderplus007/website_documentation) - The simpler predecessor that converts websites to documents without structure preservation

---

*If you find this tool helpful, consider starring the repository or contributing to its development!*