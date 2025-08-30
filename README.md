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


### Start a new chat session
```bash
curl -X POST http://localhost:8714/chat/start
```
this will return a **thread_id** that you must save it, so you can continue chat.

example output:
```bash
{
  "answer": "سلام! من یک ربات پزشکی هستم. چگونه می توانم به شما کمک کنم؟",
  "thread_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Send a message to an existing chat session
```bash
curl -X POST http://localhost:8714/chat/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "علایم بیماری کوید چیست؟", "thread_id": "your-thread-id-here"}'
```

example output:
```bash
{
  "answer": "chatbot response",
  "thread_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

If you send invalid thread_id:
```bash
{
  "detail": "Invalid thread ID"
}
```

if you send empty prompt:
```bash
{
  "detail": "Empty prompt received"
}
```

if you send empty string ("") thread_id or null thread_id, a new chat session will be started with following output:
```bash
{
  "answer": "سلام! من یک ربات پزشکی هستم. چگونه می توانم به شما کمک کنم؟",
  "thread_id": "123e4567-e89b-12d3-a456-426614174000"
}
```


### List all active sessions
```bash
curl -X GET http://localhost:8714/sessions
```

example output:
```bash
{
  "active_sessions": [
    "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
    "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9"
  ]
}
```


### Delete a chat session
```bash
curl -X DELETE http://localhost:8714/chat/delete/your-thread-id-here
```

Success Response:
```bash
{
  "message": "Session deleted successfully",
  "thread_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
}
```

Error Response (if thread_id doesn't exist):
```bash
{
  "detail": "Session not found"
}
```