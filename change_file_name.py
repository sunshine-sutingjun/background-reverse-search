import os
import re

def natural_sort_key(s):
    """
    Generate a sorting key for a given string that allows natural sorting (numerical order).

    Args:
        s (str): The string to be sorted.

    Returns:
        list: A list containing a mix of integers and strings for natural sorting.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def batch_rename_files_sorted(directory, suffix):
    """
    Rename files in a directory in a sorted order with a specified suffix.

    Args:
        directory (str): The directory containing the files to be renamed.
        suffix (str): The file suffix to use in the renamed files.
    """
    # Retrieve and sort filenames using natural sort
    filenames = sorted(
        (f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))),
        key=natural_sort_key
    )

    # Rename files with a numerical prefix and specified suffix
    for index, filename in enumerate(filenames, start=1):
        old_path = os.path.join(directory, filename)
        new_filename = f"{index}.{suffix}"
        new_path = os.path.join(directory, new_filename)

        os.rename(old_path, new_path)
        print(f"Renamed '{filename}' to '{new_filename}'")

# Example usage
suffix = 'jpg'
directory_path = './background/train/image/ant'
batch_rename_files_sorted(directory_path, suffix)
