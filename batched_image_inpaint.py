import os
import cv2
from tqdm import tqdm

def get_sorted_folders(directory):
    """
    Return a sorted list of folder names in the specified directory.

    Args:
        directory (str): The directory to list folders from.

    Returns:
        list: Sorted list of folder names.
    """
    folders = [item for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item))]
    return sorted(folders)

def inpaint_image_background(image_path, mask_path, save_path):
    """
    Inpaint the object area in the image using the mask and save the result.
    Does not overwrite existing files at save path.

    Args:
        image_path (str): Path to the source image.
        mask_path (str): Path to the mask image.
        save_path (str): Path to save the inpainted image.
    """
    if os.path.exists(save_path):
        return

    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    if image.shape[:2] != mask.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)

    inpaint_radius = 3
    inpainted_image = cv2.inpaint(image, mask, inpaint_radius, cv2.INPAINT_TELEA)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, inpainted_image)


def process_directory_images(base_dir):
    """
    Process all images in the specified base directory for inpainting.

    Args:
        base_dir (str): Base directory containing images and masks.
    """
    image_dir = os.path.join(base_dir, 'train', 'image')
    mask_dir = os.path.join(base_dir, 'train', 'groundtruth')
    save_dir = os.path.join(base_dir, 'background_transformed', 'train', 'image')

    categories = get_sorted_folders(image_dir)

    for category in categories:
        category_image_dir = os.path.join(image_dir, category)
        category_mask_dir = os.path.join(mask_dir, category)
        category_save_dir = os.path.join(save_dir, category)

        filenames = os.listdir(category_image_dir)
        for filename in tqdm(filenames, desc=f"Processing {category}"):
            if filename.endswith('.jpg'):
                image_path = os.path.join(category_image_dir, filename)
                mask_filename = filename.replace('.jpg', '.png')
                mask_path = os.path.join(category_mask_dir, mask_filename)
                save_path = os.path.join(category_save_dir, filename)

                inpaint_image_background(image_path, mask_path, save_path)

# Example usage
base_dir = './CoCOD8K'
process_directory_images(base_dir)
