import subprocess
import os
import signal
import time

def run_fastapi():
    """run FastAPI using uvicorn"""
    return subprocess.Popen(["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_streamlit():
    """run Streamlit app"""
    return subprocess.Popen(["streamlit", "run", "web/streamlit_app.py"])

if __name__ == "__main__":
    print("Starting FastAPI...")

    # Start fastAPI
    fastapi_process = run_fastapi()
    time.sleep(15)#give FastAPI some time to start
    
    print("Starting Streamlit...")
    streamlit_process = run_streamlit()

    try:
        #keep the script running while both processes are alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        # Terminate both processes on Ctrl+C
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.wait()
        streamlit_process.wait()
        print("Services stopped.")
