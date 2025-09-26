# SafeZone AI - Real-Time Safety Vest Detection Dashboard

A real-time monitoring system that uses a YOLOv8 model to detect safety vest compliance on a live video feed and displays alerts and statistics on a dynamic web dashboard.
<img width="1877" height="917" alt="image" src="https://github.com/user-attachments/assets/09c4d29d-becd-43cc-a123-060006668c65" />



## Features

- **Real-Time Detection:** Analyzes a video stream to detect workers with and without safety vests.
- **Dynamic Dashboard:** Live-updating web interface built with Flask, showing key metrics like worker counts and violation alerts.
- **Violation Logging:** Automatically logs non-compliance events into an SQLite database.
- **Snapshot on Violation:** Saves an image of the frame where a violation occurred for review.

## Tech Stack

- **Backend:** Python, Flask
- **AI Model:** YOLOv8 (Ultralytics)
- **Computer Vision:** OpenCV
- **Database:** SQLite
- **Frontend:** HTML, Tailwind CSS, JavaScript

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the application:**
    - Place your trained YOLOv8 model in the root folder as `best.pt`.
    - Place your video file in the root folder as `your_video.mp4`.
    - Update the video and model paths inside `app.py` if needed.

5.  **Run the application:**
    ```bash
    python app.py
    ```
    Open your web browser and navigate to `http://127.0.0.1:5001`.
