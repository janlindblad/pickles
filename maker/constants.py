"""
Configuration constants for the maker app.
"""

# Blurb text constraints
BLURB_TEXT_MAX_LENGTH = 35  # Maximum characters for blurb text

# Content generation character limits per category
CONTENT_LIMITS = {
    'interior': 500,
    'exterior': 500, 
    'highlights': 600,  # Highlights get more space as they're most important
    'options': 400,     # Options get less space as they're supplementary
}

# Content generation settings
CONTENT_SEPARATOR = '\n\n'# How to join multiple blurbs
CONTENT_ENDING = ''       # No ending needed since each blurb ends with a dot

# UI messaging
MESSAGES = {
    'no_matches_found': 'No content rules found for this selection. Please check the database configuration.',
    'content_generated': 'Content generated successfully.',
    'content_truncated': 'Content was truncated to fit character limits.',
}

# Default fallback content when no matches are found
FALLBACK_CONTENT = {
    'interior': '',
    'exterior': '',
    'highlights': '',
    'options': '',
}