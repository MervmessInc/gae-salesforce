#########
# PATHS #
#########

import os

# Full filesystem path to the project.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

# URL prefix for static files.
# Example: "http://www.example.com/static/"
STATIC_URL = "/static/"

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

##############
# MIME Types #
##############
MIME_JSON="application/json"
MIME_HTML="text/html"
MIME_TEXT="text/plain"
#MIME_XML="application/xml"
MIME_XML="text/xml"