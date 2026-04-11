import os


def copy_files_to_one(files_to_copy, output_file):
    """
    Copy contents from multiple files to a single output file

    Args:
        files_to_copy (list): List of file paths to copy from
        output_file (str): Path to the output file
    """
    try:
        with open(output_file, "w", encoding="utf-8") as output:
            for file_path in files_to_copy:
                try:
                    with open(file_path, "r", encoding="utf-8") as input_file:
                        # Read and write the content
                        content = input_file.read()
                        output.write(f"{'='*20}\n")
                        output.write(f"Content from: {file_path}\n")
                        output.write(f"{'='*20}\n")
                        output.write(content)
                        output.write("\n\n")
                        print(f"✓ Copied: {file_path}")

                except FileNotFoundError:
                    print(f"✗ File not found: {file_path}")
                except Exception as e:
                    print(f"✗ Error reading {file_path}: {str(e)}")

        print(f"\n✅ All files have been copied to: {output_file}")

    except Exception as e:
        print(f"✗ Error creating output file: {str(e)}")


# Example usage
if __name__ == "__main__":
    # List of files to copy (modify these paths)
    files_to_copy = ["main.py", "debtholderapp.kv"]

    # Output file
    output_file = "app.txt"

    # Copy files
    copy_files_to_one(files_to_copy, output_file)
