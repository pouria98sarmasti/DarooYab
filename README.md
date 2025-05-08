# **Setup Instructions**
## **Part 1: download and configure ollama image**
**step 1:** download ollama image
```bash
docker pull ollama/ollama:latest
```
**step 2:** run a container from ollama image and download necessary models
```bash
docker run -d --name ollama-gpu ollama/ollama:latest
```
```bash
## takes minutes to houres based on your connection speed

# llm for run app on pc
docker exec ollama-gpu ollama pull hf.co/bartowski/gemma-2-2b-it-GGUF:Q6_K_L
# llm for run app on server
docker exec ollama-gpu ollama pull hf.co/bartowski/aya-expanse-8b-GGUF:Q6_K_L
```
> ***Note:*** based on the system (pc or server) that you run the app on, comment/uncomment lines 40/41 in MedicalChatBot_v1.py script.

**step 3:** create an image from ollama-gpu container
```bash
docker commit ollama-gpu ollama-gpu:latest
```
**step 4:** stop and remove ollama-gpu container
```bash
docker rm -f ollama-gpu
```
## **Part 2:**
**step 1:** install **nvidia container toolkit** (search in google)

**step 2:** Build the medical-chatbot from Docker file
```bash
## takes minutes to houres based on your connection speed

docker build -t medical-chatbot:latest .
```

**step 3:** Run the Containers
```bash
docker-compose up -d
```

# **API Endpoints**
after runing the project, interactive api documentation will be available at this address:
```bash
http://localhost:8714/docs
```