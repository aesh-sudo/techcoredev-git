import os
print(f"Hello from Jenkins build #{os.environ.get('BUILD_NUMBER', 'unknown')}!")
