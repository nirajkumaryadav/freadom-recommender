# Freadom Book Recommendation System

## Overview
Freadom is a book recommendation system designed to suggest appropriate reading materials to children based on their interests and reading level. The system uses semantic similarity analysis to match user interests with book content and provides personalized recommendations.

## Architecture
- **Flask API Backend**: Handles recommendation requests and text analysis
- **Streamlit Frontend**: Provides UI for children, teachers, and parents
- **Semantic Analysis**: Matches user interests with book content
- **Text Analysis**: Determines reading level complexity

## Semantic Analysis Models
The system now supports two semantic analysis models:
1. **Sentence-BERT**: Default lightweight model for semantic similarity
2. **Qwen3-0.6B**: More advanced LLM model for improved semantic understanding

### Model Selection
You can switch between models using the API:
```
POST /api/settings/model
Content-Type: application/json

{
  "model": "sbert"  # or "qwen"
}
```

The UI also offers model selection for administrators in the teacher dashboard.

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Download the required models:
```
python download_models.py
```

If you encounter Hugging Face authentication issues, use your token:
```
python download_models.py --token YOUR_HUGGINGFACE_TOKEN
```

### Initialize the Database
```
python initialize_db.py
```

### Running the Application

#### Option 1: Run Directly
Run the Flask API:
```
python app.py
```

In a separate terminal, run the Streamlit frontend:
```
streamlit run streamlit_app.py
```

#### Option 2: Using Docker
```
docker-compose up -d
```

## API Endpoints

### User Endpoints
- `GET /api/users` - Get all users
- `GET /api/user/<id>` - Get user details
- `GET /api/user/<id>/progress` - Get user reading progress

### Recommendation Endpoints
- `GET /api/recommend/<user_id>` - Get personalized recommendations
- `GET /api/recommend/<user_id>?count=<n>` - Get n recommendations

### Model Selection Endpoints
- `GET /api/settings/model` - Get current semantic model
- `POST /api/settings/model` - Set semantic model

### Database Setup
- `GET /api/setup` - Initialize the database with sample data

### Model Setup
- `GET /api/setup/models` - Initialize and download AI models

## Performance Benchmarks
Run the benchmark script to compare performance between models:
```
python benchmark_models.py
```

This will generate a comparison chart showing:
- Processing time for each model
- Memory usage
- Semantic similarity scores

## Docker Deployment
The application includes Docker configurations for easy deployment:
- `Dockerfile.api` - For the Flask API backend
- `Dockerfile.streamlit` - For the Streamlit frontend
- `docker-compose.yml` - Orchestrates both containers

### Standard Deployment
Build and run with:
```
docker-compose up --build
```

### Simplified Deployment (No Model Downloads Required)
For environments where you can't download Hugging Face models, use the simplified deployment:
```
docker-compose -f docker-compose.simple.yml up --build
```

Or run the deployment script:
```powershell
# For Windows PowerShell
.\deploy-simple.ps1
```

## Troubleshooting
If you encounter issues with model downloads:
1. Create a Hugging Face account at https://huggingface.co/
2. Generate an access token at https://huggingface.co/settings/tokens
3. Use the token when downloading models:
   ```
   python download_models.py --token YOUR_TOKEN_HERE
   ```
