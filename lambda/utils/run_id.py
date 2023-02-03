"""
Helper function to generate run id
"""

from datetime import datetime
from uuid import uuid4

def generate_run_id():
    run_id = str(uuid4()) + '#' + datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    return run_id
