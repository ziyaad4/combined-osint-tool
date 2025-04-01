import os
import mimetypes
import datetime
from typing import Dict, Any, List, Optional

def extract_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from various file types.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing metadata by category
    """
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    # Determine file type using mime
    mime_type, _ = mimetypes.guess_type(file_path)
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Basic file metadata (available for all file types)
    file_stat = os.stat(file_path)
    basic_metadata = {
        "File Information": {
            "filename": os.path.basename(file_path),
            "file_size_bytes": file_stat.st_size,
            "file_size_human": format_file_size(file_stat.st_size),
            "file_extension": file_extension,
            "mime_type": mime_type or "Unknown",
            "created_time": format_timestamp(file_stat.st_ctime),
            "modified_time": format_timestamp(file_stat.st_mtime),
            "accessed_time": format_timestamp(file_stat.st_atime)
        }
    }
    
    # Extract additional metadata based on file type
    additional_metadata = {}
    
    # PDF files
    if mime_type == "application/pdf" or file_extension == ".pdf":
        additional_metadata = extract_pdf_metadata(file_path)
    
    # Image files
    elif mime_type and mime_type.startswith("image/"):
        additional_metadata = extract_image_metadata(file_path)
    
    # Office documents
    elif file_extension in [".docx", ".xlsx", ".pptx"]:
        additional_metadata = extract_office_metadata(file_path)
    
    # Merge basic metadata with file-specific metadata
    metadata = {**basic_metadata, **additional_metadata}
    
    return metadata

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def format_timestamp(timestamp: float) -> str:
    """
    Format timestamp as human-readable date and time.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted date and time string
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from PDF files.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(file_path)
        info = reader.metadata
        
        metadata = {"PDF Metadata": {}}
        
        if info:
            # Extract standard PDF metadata
            for key, value in info.items():
                # Clean up the key (remove leading '/')
                clean_key = key
                if isinstance(key, str) and key.startswith('/'):
                    clean_key = key[1:]
                
                # Format the value
                if isinstance(value, datetime.datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif value and not isinstance(value, (str, int, float, bool)):
                    value = str(value)
                
                metadata["PDF Metadata"][clean_key] = value
        
        # Add page count and other PDF-specific info
        metadata["PDF Metadata"]["page_count"] = len(reader.pages)
        
        # Extract text from first page for preview
        if reader.pages:
            first_page_text = reader.pages[0].extract_text()
            if first_page_text:
                # Limit preview text length
                preview = first_page_text[:500] + "..." if len(first_page_text) > 500 else first_page_text
                metadata["Content Preview"] = preview
        
        return metadata
    except ImportError:
        return {"PDF Metadata": {"error": "PyPDF2 library not installed"}}
    except Exception as e:
        return {"PDF Metadata": {"error": f"Failed to extract PDF metadata: {str(e)}"}}

def extract_image_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from image files.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Dictionary containing image metadata
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        image = Image.open(file_path)
        
        # Basic image information
        metadata = {
            "Image Metadata": {
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "resolution": f"{image.width}x{image.height}"
            }
        }
        
        # Extract EXIF data if available
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                
                # Format value for better readability
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except UnicodeDecodeError:
                        value = str(value)
                
                exif_data[tag] = value
            
            if exif_data:
                metadata["EXIF Data"] = exif_data
        
        return metadata
    except ImportError:
        return {"Image Metadata": {"error": "PIL library not installed"}}
    except Exception as e:
        return {"Image Metadata": {"error": f"Failed to extract image metadata: {str(e)}"}}

def extract_office_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from Microsoft Office documents.
    
    Args:
        file_path: Path to the Office document
        
    Returns:
        Dictionary containing Office document metadata
    """
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        
        file_extension = os.path.splitext(file_path)[1].lower()
        document_type = {
            ".docx": "Word Document",
            ".xlsx": "Excel Spreadsheet",
            ".pptx": "PowerPoint Presentation"
        }.get(file_extension, "Office Document")
        
        metadata = {
            f"{document_type} Metadata": {}
        }
        
        # Office Open XML files are ZIP archives containing XML files
        with zipfile.ZipFile(file_path) as zip_file:
            # List of XML files that might contain metadata
            metadata_files = [
                "docProps/core.xml",  # Core properties
                "docProps/app.xml"    # Application-specific properties
            ]
            
            for meta_file in metadata_files:
                try:
                    with zip_file.open(meta_file) as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Extract all elements and their values
                        for elem in root.iter():
                            # Remove namespace from tag name
                            tag = elem.tag.split('}')[-1]
                            
                            if elem.text and elem.text.strip():
                                metadata[f"{document_type} Metadata"][tag] = elem.text.strip()
                except (KeyError, ET.ParseError):
                    # File doesn't exist or is not valid XML
                    pass
        
        return metadata
    except ImportError:
        return {f"Office Metadata": {"error": "Required libraries not installed"}}
    except Exception as e:
        return {f"Office Metadata": {"error": f"Failed to extract Office metadata: {str(e)}"}}
