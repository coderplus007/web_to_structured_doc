#!/usr/bin/env python3
"""
Structure Detector Module

This module is responsible for analyzing web pages and identifying navigation structures
that can be converted into document chapters. It uses multiple strategies to recognize
menus and hierarchical structures on the website.
"""

import logging
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# Common CSS selectors for navigation elements
DEFAULT_SELECTORS = [
    "nav",
    ".navigation",
    ".nav",
    ".menu",
    ".sidebar",
    "#sidebar",
    ".toc",
    "#toc",
    "header .menu",
    ".main-menu",
    ".navbar",
    "ul.navigation",
    ".doc-menu",
    ".site-menu"
]

class StructureDetector:
    """Detects and analyzes menu structures on web pages"""
    
    def __init__(self, selector=None, config_path=None):
        """Initialize the detector with optional custom selector or configuration"""
        self.custom_selector = selector
        self.selectors = self._load_selectors(config_path)
        self.structure = {}  # Dictionary to store the hierarchical structure
    
    def _load_selectors(self, config_path):
        """Load selectors from configuration file or use defaults"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading selectors from {config_path}: {e}")
        
        return DEFAULT_SELECTORS
    
    def detect_structure(self, html_content, base_url):
        """
        Analyze the HTML content to detect menu structure
        
        Args:
            html_content (str): HTML content of the page
            base_url (str): Base URL of the page for resolving relative links
            
        Returns:
            dict: Hierarchical structure of the site navigation
        """
        if not html_content:
            return {}
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # First try custom selector if provided
        if self.custom_selector:
            menu_element = soup.select_one(self.custom_selector)
            if menu_element:
                return self._extract_structure(menu_element, base_url)
        
        # Try each of the common selectors
        for selector in self.selectors:
            menu_elements = soup.select(selector)
            if menu_elements:
                # Find the most likely navigation element (one with the most links)
                best_element = max(menu_elements, key=lambda el: len(el.find_all('a')), default=None)
                if best_element and len(best_element.find_all('a')) > 2:  # At least 3 links to be considered a menu
                    structure = self._extract_structure(best_element, base_url)
                    if structure:
                        return structure
        
        # If no structure found with selectors, try heuristic detection
        return self._heuristic_detection(soup, base_url)
    
    def _extract_structure(self, menu_element, base_url):
        """
        Extract hierarchical structure from a menu element
        
        Args:
            menu_element: BeautifulSoup element containing the menu
            base_url (str): Base URL for resolving relative links
            
        Returns:
            dict: Hierarchical structure with URLs and titles
        """
        structure = {}
        
        # Process lists, which are common navigation structures
        for list_item in menu_element.find_all(['li']):
            # Find the anchor in this list item
            anchor = list_item.find('a')
            if not anchor or not anchor.get('href'):
                continue
            
            title = anchor.get_text(strip=True)
            url = urljoin(base_url, anchor.get('href'))
            
            # Skip empty or fragment-only links
            if not title or url.endswith('#') or url == base_url + '#':
                continue
            
            # Check for nested lists, which indicate submenus
            submenus = list_item.find_all(['ul', 'ol'])
            if submenus:
                # This item has children
                children = {}
                for submenu in submenus:
                    for sub_item in submenu.find_all('li'):
                        sub_anchor = sub_item.find('a')
                        if not sub_anchor or not sub_anchor.get('href'):
                            continue
                        
                        sub_title = sub_anchor.get_text(strip=True)
                        sub_url = urljoin(base_url, sub_anchor.get('href'))
                        
                        if not sub_title or sub_url.endswith('#'):
                            continue
                        
                        # Check for further nesting
                        sub_submenus = sub_item.find_all(['ul', 'ol'])
                        if sub_submenus:
                            sub_children = {}
                            # Process deeper levels recursively
                            for sub_submenu in sub_submenus:
                                self._process_submenu(sub_submenu, base_url, sub_children)
                            children[sub_title] = {'url': sub_url, 'title': sub_title, 'children': sub_children}
                        else:
                            children[sub_title] = {'url': sub_url, 'title': sub_title}
                
                structure[title] = {'url': url, 'title': title, 'children': children}
            else:
                # This is a leaf item
                structure[title] = {'url': url, 'title': title}
        
        return structure

    def _process_submenu(self, submenu, base_url, parent_dict):
        """Process a submenu recursively to extract deeper structure levels"""
        for item in submenu.find_all('li', recursive=False):
            anchor = item.find('a')
            if not anchor or not anchor.get('href'):
                continue
            
            title = anchor.get_text(strip=True)
            url = urljoin(base_url, anchor.get('href'))
            
            if not title or url.endswith('#'):
                continue
            
            nested = item.find(['ul', 'ol'])
            if nested:
                children = {}
                self._process_submenu(nested, base_url, children)
                parent_dict[title] = {'url': url, 'title': title, 'children': children}
            else:
                parent_dict[title] = {'url': url, 'title': title}
    
    def _heuristic_detection(self, soup, base_url):
        """
        Use heuristics to detect navigation when standard selectors fail
        
        This tries various approaches:
        1. Look for groups of links in containers
        2. Detect sections with high link density
        3. Find common navigation patterns in the page structure
        
        Args:
            soup: BeautifulSoup object of the page
            base_url (str): Base URL for resolving relative links
            
        Returns:
            dict: Detected navigation structure, or empty dict if none found
        """
        # Strategy 1: Find containers with multiple links
        containers = soup.find_all(['div', 'nav', 'section', 'aside'])
        link_containers = [(container, len(container.find_all('a'))) for container in containers]
        link_containers.sort(key=lambda x: x[1], reverse=True)
        
        for container, link_count in link_containers:
            if link_count >= 5:  # Container with significant number of links
                # Check if links are grouped logically
                result = self._analyze_link_container(container, base_url)
                if result:
                    return result
        
        # Strategy 2: Find header sections that might contain navigation
        headers = soup.find_all(['header', '.header', '#header'])
        for header in headers:
            links = header.find_all('a')
            if len(links) >= 3:
                result = self._extract_links_structure(links, base_url)
                if result:
                    return result
        
        # Strategy 3: Look for any section with high link density that might be a table of contents
        high_density_sections = self._find_high_link_density_sections(soup)
        for section in high_density_sections:
            result = self._extract_links_structure(section.find_all('a'), base_url)
            if result:
                return result
        
        # No structure detected
        return {}
    
    def _analyze_link_container(self, container, base_url):
        """Analyze a container with multiple links to detect structure"""
        # Check if container has list elements, which typically indicate menu structure
        lists = container.find_all(['ul', 'ol'])
        if lists:
            return self._extract_structure(container, base_url)
        
        # If no lists, try to detect structure from the links directly
        links = container.find_all('a')
        return self._extract_links_structure(links, base_url)
    
    def _extract_links_structure(self, links, base_url):
        """Extract structure from a flat list of links"""
        structure = {}
        
        for link in links:
            title = link.get_text(strip=True)
            url = urljoin(base_url, link.get('href', ''))
            
            # Skip empty or fragment-only links
            if not title or not url or url.endswith('#') or url == base_url + '#':
                continue
                
            # Check if this link text suggests it's a category
            if self._is_likely_category(title, link):
                # This is likely a category heading
                structure[title] = {'url': url, 'title': title, 'is_category': True}
            else:
                # Regular link
                structure[title] = {'url': url, 'title': title}
        
        return structure
    
    def _is_likely_category(self, title, element):
        """Determine if a link is likely a category header based on text and styling"""
        # Text-based heuristics (category-like words)
        category_indicators = ['category', 'section', 'chapter', 'guide', 'overview', 'introduction', 'getting started']
        if any(indicator in title.lower() for indicator in category_indicators):
            return True
        
        # Check parent elements for header tags
        if element.parent and element.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return True
            
        # Check for styling that might indicate a heading (font-weight, text-transform)
        styles = element.get('style', '')
        if 'bold' in styles or 'font-weight' in styles or 'text-transform: uppercase' in styles:
            return True
            
        # Check for classes that might indicate a heading
        classes = element.get('class', [])
        heading_classes = ['heading', 'header', 'title', 'category', 'section-title']
        if any(cls in heading_classes for cls in classes):
            return True
            
        return False
    
    def _find_high_link_density_sections(self, soup):
        """Find sections of the page with high link density that might be navigation"""
        sections = []
        
        # Check all divs and other containers
        containers = soup.find_all(['div', 'section', 'aside', 'nav'])
        
        for container in containers:
            # Calculate link density (links per text character)
            links = container.find_all('a')
            text_length = len(container.get_text())
            
            if text_length > 0 and len(links) >= 3:
                link_density = len(links) / text_length
                
                # High link density is often navigation
                if link_density > 0.05:
                    sections.append(container)
        
        return sections
                
    def get_structure_depth(self, structure, current_depth=1):
        """
        Calculate the maximum depth of the menu structure
        
        Args:
            structure (dict): Menu structure dictionary
            current_depth (int): Current depth level
            
        Returns:
            int: Maximum depth of the structure
        """
        if not structure:
            return 0
            
        max_depth = current_depth
        
        for item, details in structure.items():
            if 'children' in details and details['children']:
                child_depth = self.get_structure_depth(details['children'], current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def flatten_structure(self, structure, current_level=1, parent_path=None):
        """
        Convert hierarchical structure to a flat list with level information
        
        Args:
            structure (dict): Hierarchical structure dictionary
            current_level (int): Current level in the hierarchy
            parent_path (list): Path of parent items
            
        Returns:
            list: Flat list of pages with their hierarchy information
        """
        if not structure:
            return []
            
        flat_list = []
        parent_path = parent_path or []
        
        for title, details in structure.items():
            url = details.get('url', '')
            current_path = parent_path + [title]
            
            item = {
                'title': title,
                'url': url,
                'level': current_level,
                'path': current_path,
                'is_category': details.get('is_category', False)
            }
            
            flat_list.append(item)
            
            if 'children' in details and details['children']:
                children = self.flatten_structure(
                    details['children'], 
                    current_level + 1, 
                    current_path
                )
                flat_list.extend(children)
        
        return flat_list
