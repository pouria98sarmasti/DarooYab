# Use an official PyTorch image with CUDA support
FROM docker.arvancloud.ir/pytorch/pytorch:2.6.0-cuda12.6-cudnn9-runtime

# Set environment variables for Python and CUDA
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
# ENV CUDA_VISIBLE_DEVICES=0
## default behavior is to use all GPUs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r /app/reqirements.txt

# Download and cache the embedding model during build
RUN python3 -c "from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings; \
    import torch; \
    device = 'cuda' if torch.cuda.is_available() else 'cpu'; \
    HuggingFaceEmbeddings(model_name='jinaai/jina-embeddings-v3', \
    model_kwargs={'device': device, 'trust_remote_code': True}, \
    encode_kwargs={'normalize_embeddings': False})"

# Set the working directory
WORKDIR /app

# Create FAISS database during build
RUN python3 vectorDB_from_Dataset.py

# Expose the FastAPI port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "api_ChatBot_v1:app", "--host", "0.0.0.0", "--port", "8000"]