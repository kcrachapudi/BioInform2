import os
import shutil

def clean_folder(path, remove_dirs=False):
    if not os.path.exists(path):
        os.makedirs(path)
        return

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path) and remove_dirs:
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Error deleting {item_path}: {e}")


def cleanup():
    print("🧹 Cleaning BioInform2 project...")

    clean_folder("results")
    clean_folder("logs")
    clean_folder("work", remove_dirs=True)

    print("✅ Cleanup complete!")


if __name__ == "__main__":
    cleanup()