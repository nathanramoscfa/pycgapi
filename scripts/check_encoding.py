import os


def is_utf8(fname):
	try:
		with open(fname, 'r', encoding='utf-8') as f:
			f.read()
		return True
	except UnicodeDecodeError:
		return False


def contains_hidden_chars(fname):
	with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
		content = f.read()
		return any(0 < ord(char) < 32 for char in content if char not in '\r\n\t')


def check_project_files(root_dir):
	# List of file extensions to check
	extensions_to_check = ['.py', '.md', '.rst', '.txt']

	# Walk through the project directory
	for subdir, dirs, files in os.walk(root_dir):
		for file in files:
			filepath = os.path.join(subdir, file)
			if any(filepath.endswith(ext) for ext in extensions_to_check):
				# Check if file is UTF-8 encoded
				utf8_check = is_utf8(filepath)
				# Check for hidden characters
				hidden_char_check = contains_hidden_chars(filepath)
				print(f"File: {filepath}")
				print(f" - UTF-8 Encoded: {'Yes' if utf8_check else 'No'}")
				print(f" - Contains Hidden Characters: {'Yes' if hidden_char_check else 'No'}")
				if not utf8_check or hidden_char_check:
					print(f" - Warning: Potential encoding issues detected in {filepath}\n")
				else:
					print(" - File seems fine\n")


if __name__ == "__main__":
	# Set the project root to the parent directory of this script
	project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	check_project_files(project_root)
