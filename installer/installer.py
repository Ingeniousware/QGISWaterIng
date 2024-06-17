import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def check_and_install(package_name):
    try:
        # Attempt to import the package to see if it's already installed
        __import__(package_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        # If the package is not installed, install it
        print(f"Installing {package_name}...")
        install_package(package_name)
        print(f"{package_name} installed successfully.")

# Check and install signalrcore
check_and_install('signalrcore')

# Check and install wntr
check_and_install('wntr')
