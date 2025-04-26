import logging
import sys

def setup_logging(debug=False):
    """設置 log"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
        encoding="utf-8",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger('paramiko').setLevel(logging.DEBUG) if debug else logging.getLogger('paramiko').setLevel(logging.WARNING) 

