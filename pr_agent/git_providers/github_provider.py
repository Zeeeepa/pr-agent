import copy
import difflib
import hashlib
import itertools
import re
import time
import traceback
import json
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urlparse

from github.Issue import Issue
from github import AppAuthentication, Github, GithubException
from retry import retry
from starlette_context import context

from ..algo.file_filter import filter_ignored
from ..algo.git_patch_processing import extract_hunk_headers
from ..algo.language_handler import is_valid_file
from ..algo.types import EDIT_TYPE
from ..algo.utils import (PRReviewHeader, Range, clip_tokens,
                          find_line_number_of_relevant_line_in_file,
                          load_large_diff, set_file_languages)
from ..config_loader import get_settings
from ..log import get_logger
from ..servers.utils import RateLimitExceeded
from .git_provider import (MAX_FILES_ALLOWED_FULL, FilePatchInfo, GitProvider,
                           IncrementalPR)
