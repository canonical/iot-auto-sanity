"""decorate console output message"""

import shutil

columns = shutil.get_terminal_size().columns


def gen_head_string(title):
    """Adjust how message be showen"""
    return f"======== {title} ========".center(columns)
