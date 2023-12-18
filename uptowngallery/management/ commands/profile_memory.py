import os
import fnmatch
from django.core.management.base import BaseCommand
from memory_profiler import profile


class Command(BaseCommand):
    help = "Profile memory usage for my Django code"

    def handle(self, *args, **options):
        # Define the root directory of my Django project
        root_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # Define a list of file patterns to match (e.g., "*.py" for Python files)
        file_patterns = ["*.py"]

        # Recursively search for files matching the patterns
        for root, _, files in os.walk(root_dir):
            for pattern in file_patterns:
                for filename in fnmatch.filter(files, pattern):
                    # Construct the full path of the file
                    file_path = os.path.join(root, filename)

                    # Check if the file is not this management command file itself
                    if file_path != os.path.abspath(__file__):
                        # Profile the memory usage of the code in the file
                        self.stdout.write(f"Profiling: {file_path}")
                        with open(file_path, "rb") as f:
                            code = compile(f.read(), file_path, "exec")
                            exec(code, {}, {})
