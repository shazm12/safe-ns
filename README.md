
# Safe-NS:Multi-Modal Content Moderator (Image & Text) (Mid Weightage in Evaluation)

# Overview

**A multi-agent system for detecting NSFW and toxic content in text & images.**

### **Agents**

1. **Main Agent** (Llama3-70B)
    - Orchestrates moderation flow
    - Generates final reports & summaries
2. **NSFW Agent** (Google Vision API)
    - Detects explicit/suggestive images
    - Flags nudity, violence, and graphic content
3. **Toxicity Agent** (Llama3-70B)
    - Identifies hate speech, harassment, and toxic text
    - Analyzes context for nuanced language

### **How It Works**

1. User submits text/image
2. Main Agent routes content to appropriate detectors
3. NSFW Agent scans images, Toxicity Agent checks text
4. Main Agent compiles results and returns a moderation decision

## Built using

- Frontend: Next.js
- Backend: FastAPI
- Infrastructure: Groq AI for fast inference.


# Plan

### Core Components

- **Frontend Interface**: React-based web application for content upload and results display
- **Backend API**: Fast API server handling content processing
- **Image Analysis Pipeline**: NSFW detection + OCR extraction
- **Text Analysis Pipeline**: Toxicity, hate speech, and PII detection
- **Decision Engine**: Aggregates results and provides safety verdicts

# Functioning of AI Agent

1. **Image/Text Input**: The system receives an image for analysis.
2. **AI Analysis Pipeline**:
    - **OCR Processing**: An OCR agent extracts all text from the image
    - **Content Safety Check**: A NSFW detection agent scans for inappropriate visual content
    - **Text Toxicity Analysis**: If text is found or input was text, a toxicity agent evaluates it for offensive language, slurs, or harmful content
3. **Result Compilation**: The system combines findings from all checks into a comprehensive safety report
4. **Final Review**: A master LLM agent synthesizes the data into a clear, human-readable summary indicating:
    - Overall safety status (Safe/Unsafe)
    - Specific reasons for any unsafe classification
    - Excerpts of problematic content (when applicable)
5. **Output Delivery**: The finalized safety assessment is returned to the user.

```mermaid
%%{init: {'theme': 'neutral', 'fontFamily': 'Arial', 'gantt': {'barHeight': 20}}}%%
flowchart TD
    A[Image/Text Input] --> B[Main Agent]
    B --> |Text| F
    B --> |Image| C[OCR Agent Text Extraction]
    B --> |Image| D[NSFW Detection Agent Visual Content Check]
    C --> E{Text Found?}
    E -->|Yes| F[Toxicity Agent Offensive Language Check]
    E -->|No| G[No Text Analysis]
    D --> H
    G --> H
    F --> H[Compile Results]
    H --> I[Main Agent]
    I --> J{{Generate Final Report}}
    J --> K[Output: Safety Assessment]
    
    style A fill:#4CAF50,stroke:#388E3C,color:white
    style B fill:#2196F3,stroke:#1976D2,color:white
    style C fill:#607D8B,stroke:#455A64,color:white
    style D fill:#607D8B,stroke:#455A64,color:white
    style F fill:#FF9800,stroke:#F57C00,color:black
    style K fill:#4CAF50,stroke:#388E3C,color:white
    style I fill:#2196F3,stroke:#1976D2,color:white
    
    classDef agent fill:#607D8B,stroke:#455A64,color:white
    class C,D,F agent
```

# Components of the Project

# Main Agent

The main agent is responsible to call the other agents like the OCR, NSFW and Toxicity agent to check the images and text for NSFW content and also prepare a summarized report from the analysis data that it gets from all agents.

It does this by using the Mistral model with relevant context to suummarize and reason for the conent being NSFW and also highlight words which fall under NSFW or catrgory of NSFW for the case of images.

## OCR Recognition

- We let tesarract library choose the best model for the task. (mostly LSTM neural nets)
- We choose to process text in images as single text columns or blocks which is best for the case of dealing with images.

# NSFW Agent

- We used Google Vision API’ Safe Search capability to detect NSFW content. Below listed are its key features:
1. **Safe Search Detection**
    
    The primary feature for detecting NSFW content is **Safe Search**, which categorizes images based on the likelihood of containing:
    
    - **Adult content** (nudity, sexual activity)
    - **Violence** (graphic or disturbing violent scenes)
    - **Medical content** (blood, injuries, medical procedures)
    - **Spoof content** (parody, fake, or manipulated media)
    - **Racy content** (provocative or suggestive imagery)
2. **Confidence Scoring**
    
    Each category is assigned a confidence score (**`VERY_UNLIKELY`**, **`UNLIKELY`**, **`POSSIBLE`**, **`LIKELY`**, **`VERY_LIKELY`**), allowing you to set thresholds for filtering.
    
3. **Multi-Format Support**
    
    Works with JPEG, PNG, GIF, BMP, and WEBP images, as well as frames from videos.
    
4. **Integration with Google Cloud**
    
    Can be used alongside other Google Cloud services like **Cloud Storage, AutoML Vision**, or **Vertex AI** for custom models.
    

# Toxicity Agent

- Toxicity Agent is the agent responsible to find offensive text content on the basis of given categories below:
    1. Explicit profanity
    2. Hate speech
    3. Threats
    4. Sexual content
    5. Harassment

- We used Langchain to create a single chain to take Llama LLM model(llama3-70b) through Groq API with context prompt set as per the use case and we get the results in json format which we reconcile with other result from model to generate a overall report.

# Problems I faced during project

## Image Recognition and Object Detection

While the Google’s Vision API is doing a very good job with detect NSFW images, in some cases it is not able to infer the correct category of NSFW content and also object detection is also not working as good as I expected to and at times not able to detect objects in the image.

Hence, i figured I should work on doing some image preprocessing before sending to the Cloud Vision, here’s what I have listed till now to do:

1. Compress very high resolution images for saving cost.😅
2. Improve blurry ,very low res and darker images using OpenCV.
3. Improve contours, edges and sharpness of objects in images for better recognition.

## Reference

- https://www.philippe-fournier-viger.com/dspr/dspr32-1.pdf
- https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10510278

## Pipeline Steps

This pipeline automatically prepares images for computer vision tasks by:

1. **Smart Resizing**
    - Makes images smaller if needed (but never stretches them)
    - Keeps the original proportions intact
2. **Quality Enhancement**
    - Improves brightness and contrast automatically
    - Makes details sharper without looking unnatural
3. **Noise Reduction**
    - Cleans up graininess and small imperfections
    - Preserves important edges and textures
4. **Automatic Corrections**
    - Fixes rotated photos (using the camera's orientation data)
    - Works for both color and black-and-white images
5. **Standardized Output**
    - Ensures all images have consistent quality
    - Prepares them perfectly for AI analysis

```mermaid
graph TD
    A[Input Image] --> B[Load & Orient]
    B --> C{Color?}
    C -->|Yes| D[Convert RGB→BGR]
    C -->|No| E[Process Grayscale]
    D --> F[Smart Resize]
    E --> F
    F --> G[Quality Optimization]
    G --> H[Apply Filters]
    H --> I[Normalize]
    I --> J[Convert BGR→RGB]
    J --> K[Output Image]
```

## Inference 

Initally I was running the Llama model locally on my machine when using it and the problem was that my computer not being a super computer with good amount of GPU and RAM, the inferences from the model were taking almost a minute which would also be the case when I decide to deploy on a lambda or a normal web server or else i need to configure a very powerful server(EC2 preferbly) with good GBs of RAM and a powerful GPU.

VERY COSTLY AND TIME CONSUMING TO DEPLOY!!

Hence, with some research, I came across Groq AI - A Fast AI inference Library where they have custom hardware with all the popular open source models hosted on them and provide a simple API interface using SDKs or direct API links to use these models and get inferences in much low latency and high throughput( sometimes getting responses in 100ms).

# Deployment

- The frontend is hosted on [Vercel](https://vercel.com/).
- The backend is hosted as a web service on [Render](https://render.com/) via docker containerization.


# 🧊 Cold Start Notice

This app is deployed on [Render’s free tier](https://render.com/), which can result in cold starts. This may lead to initial response times of up to a minute after a period of inactivity. Subsequent requests will respond much faster.

At times you might get 504 Gateway timeout response, if so you can try another request after that and it would work fine. This happens due to very long cold start times.


# Backend Dev Setup

This guide will help you set up the FastAPI backend server with pytesseract OCR capabilities.

## Prerequisites

- Python 3.8 or higher
- Git
- Tesseract OCR engine

## Step 1: Install Tesseract OCR

### Windows
1. Download Tesseract installer from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and note the installation path (usually `C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to your system PATH or note the path for later configuration

### macOS
```bash
# Using Homebrew
brew install tesseract

# Using MacPorts
sudo port install tesseract
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install tesseract tesseract-devel

# Fedora
sudo dnf install tesseract tesseract-devel
```

## Step 2: Clone the Repository

```bash
git clone https://github.com/shazm12/repello-task.git
cd repello-task
```

## Step 3: Navigate to Backend Directory

```bash
cd backend
```

## Step 4: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## Step 5: Install Dependencies

In the root of backend directory, there is requirement.txt provided, you can use it with this command below:

```bash
pip install -r requirements.txt
```


## Step 6: Configure Tesseract Path (Windows Only)

If you're on Windows, you may need to specify the Tesseract path in your env file:

```bash
# For Windows
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe 

# For Linux
TESSERACT_PATH=C:\Program /usr/bin/tesseract


```


## Step 8: Run the FastAPI Server

```bash
# Basic run
uvicorn app.main:app --reload

# Run with custom host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at:
- Local: http://127.0.0.1:8000
- Network: http://0.0.0.0:8000
- API Documentation: http://127.0.0.1:8000/docs


# Setting up Groq AI and Google Cloud Vision

Note: use the sample .env.copy file to create your .env file.

## Groq AI

1. Sign Up on the GROQ Website
    Visit [GROQ's official website](https://groq.com/) (or their developer portal if available).

    Look for a "Sign Up" or "Get API Key" option.
        <br />

2. Access the API Key Section
    Once logged in, navigate to the API Keys section (usually found in the account dashboard or developer settings).

    <br />

3. Generate a New API Key
    Click on "Create API Key" or a similar button.

    Give the key a name (e.g., "My Project").

    Copy the generated key immediately (it may not be shown again).
   
    <br />

4. Set the Groq API key in the .env file in backend with GROQ_API_KEY.

## Google Cloud Vision API
Step 1: Set Up a Google Cloud Project
       
        - Go to Google Cloud Console
        
        - Visit Google Cloud Console.
        
        - Sign in with your Google account.
        
        - Create a New Project
        
        - Click on the project dropdown (top-left) → "New Project".
        
        - Enter a Project Name (e.g., "VisionAPIDemo").
        
        - Click "Create".

Step 2: Enable the Google Vision API
        
        - Open the API Library
        
        - From the left sidebar, go to "APIs & Services" → "Library".
        
        - Search for "Cloud Vision API"
        
        - Type "Cloud Vision API" in the search bar.
        
        - Click on the API from the results.
        
        - Enable the API
        
        - Click the "Enable" button.

Step 3.1: Create a Service Account(Recommended)
        
        - Go to API An Services from sidebar or search.
        
        - Go to credentials.
        
        - Click on manage service account.
        
        - Click on create new service account.
        
        - Optional: Add a description.
        
        - Click "Create and Continue".

Step 3.2: Create an API Key
        
        - Go to API An Services from sidebar or search.
        
        - Go to credentials.
        
        - Click on create new credentials.
        
        - Click on API Key.

        - You will get the key Copy and then follow other steps.
        

Step 4: Assign Roles(For Service Account only)
    
    - Under "Grant this service account access to project", assign roles:
    
    - Select "Basic" → "Viewer" (minimum).
    
    - For full access, choose "Project" → "Owner" (not recommended for - security).
    
    - Click "Continue".
    
    - Generate a JSON Key
    
    - Under "Grant users access to this service account", skip (unless needed).
    
    - Click "Done".
    
    - Now, find your service account in the list → Click the three dots (⋮) → - "Manage Keys".
    
    - Click "Add Key" → "Create New Key".
    
    - Select JSON → Click "Create".
    
    - The key file (service-account-key.json) will download automatically.
    
Step 5: Update environmental vars with key or service account

    - If Service account, store it locally and mention the location of the file in `.env` and `docker-compose.yml` under GOOGLE_APPLICATION_CREDENTIALS. Also uncomment the line in `nsfw_agent.py` for same accordingly.
    
    - If API KEY, update the `env` and `docker-compose.yml` under GOOGLE_API_KEY, check in `nsfw_agent.py` if the code is accessing the key from environmental variables.

# Setup Backend Service with Docker(Easier)
Use docker compose to create image and run the container by using this single command in the root of `backend` directory:
```bash
docker-compose up --build
```

**Note:** Keep in mind in `docker-compose.yml`, set the environment variables accordingly like groq API key and location of the service account credentials file.

For service account credentials, the suggestion would be to keep it just in the root of the `backend` directory and so you just need to pass the file path as: `your-google-service-account.json` both in the Dockerfile(do not forget to make changes in Dockerfile) and in `docker-compose.yml`.

For API Key, just update the docker-compose file in the **environment** section, the API key under GOOGLE_API_KEY.



# Next.js Frontend Setup Guide

This guide will help you set up the Next.js frontend application for the project.

## Prerequisites

- Node.js 18.17 or higher
- npm, yarn, pnpm, or bun package manager
- Git

## Step 1: Check Node.js Installation

```bash
# Check Node.js version
node --version

# Check npm version
npm --version
```

If Node.js is not installed, download it from [nodejs.org](https://nodejs.org/).

## Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

## Step 4: Install Dependencies

Choose your preferred package manager:

### Using npm
```bash
npm install
```


## Step 5: Run in Developement server
### Using npm
```bash
npm run dev
```
## Step 6: Update the Environment Variables

- Create a `.env.local` file(sample given to copy)

- Then change the API_URL to the URL of the locally running backend service.


# Secruity and Measures
--- 
## Prompt Injection Detector
This prompt injection detector checks user inputs for suspicious patterns that might try to manipulate AI systems. It looks for phrases that attempt to override instructions, execute commands, access sensitive data, or change system behavior. When it detects these red flags (like "ignore previous instructions" or code execution attempts), it raises an error to block the input. This helps prevent users from tricking AI systems into doing unintended things. The detector uses simple pattern matching to catch common attack methods.

---
## CORS
The CORS middleware has been added to FastAPI server with basic configurations, for more security we can add a proxy server like Nginx and add the origin and host of the proxy server which will get all the requests from client and redirect to the server. This is yet to be implemented.

---
# Proxy Backend Requests From Client
Well, this is automatically being taken care by Next.js where the server actions I have written to call my FastAPI server is being proxied through so when someone would try to inspect the network request to know the backend service URL , it would show the same frontend URL and this secures my backend service from various attacks like DDos Attack and various other attacks as this information is also not relevant to be known by end users.


