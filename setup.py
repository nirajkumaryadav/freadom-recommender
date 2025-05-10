# Setup script for Freadom Recommender with Qwen3-0.6B integration

import os
import sys
import subprocess
import time

def setup_environment():
    """Set up the environment for Freadom Recommender"""
    print("====================================================")
    print("    Freadom Book Recommender Setup with Qwen3-0.6B  ")
    print("====================================================")
    
    # Create a virtual environment (optional)
    create_venv = input("Would you like to create a virtual environment? (y/n): ").lower() == 'y'
    
    if create_venv:
        print("\nCreating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "freadom_venv"])
        
        # Activate virtual environment
        if os.name == "nt":  # Windows
            activate_script = os.path.join("freadom_venv", "Scripts", "activate")
            print(f"\nTo activate the virtual environment, run: {activate_script}")
            print("Then run this setup script again.")
            return False
        else:  # Unix/Linux/Mac
            activate_script = os.path.join("freadom_venv", "bin", "activate")
            print(f"\nTo activate the virtual environment, run: source {activate_script}")
            print("Then run this setup script again.")
            return False
    
    # Install requirements
    print("\nInstalling required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Download models
    print("\nDownloading models (this may take some time)...")
    try:
        subprocess.run([sys.executable, "download_models.py"])
    except Exception as e:
        print(f"Error downloading models: {e}")
        print("You can try downloading models manually later using 'python download_models.py'")
    
    # Initialize database
    print("\nInitializing database...")
    try:
        subprocess.run([sys.executable, "initialize_db.py"])
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("You can try initializing the database manually later using 'python initialize_db.py'")
    
    print("\n====================================================")
    print("    Setup complete!                                 ")
    print("====================================================")
    
    print("\nTo run the application:")
    print("1. Start the Flask API server:")
    print("   python app.py")
    print("\n2. In a separate terminal, start the Streamlit frontend:")
    print("   python run_streamlit.py")
    print("\n3. Open your browser and navigate to:")
    print("   http://localhost:8501")
    
    return True

if __name__ == "__main__":
    setup_environment()
