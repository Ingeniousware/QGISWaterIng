import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

try:
    # Attempt to import the package to see if it's already installed
    import signalrcore
    print("signalrcore is already installed.")
except ImportError:
    # If the package is not installed, install it
    print("Installing signalrcore...")
    install_package('signalrcore')
    print("signalrcore installed successfully.")
