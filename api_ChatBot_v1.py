from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from MedicalChatBot_v1 import create_chatBot_app

app = FastAPI(title="Medical Chatbot API")


class ChatRequest(BaseModel):
    prompt: str
    thread_id: Optional[str] = None  # For continuing conversations

class ChatResponse(BaseModel):
    answer: str
    thread_id: str


# Store chat sessions in memory
chat_sessions = {}
def initialize_chat_session(thread_id: str):
    """
    The function creates a new chat session with memory for a given thread ID.
    
    Args:
      thread_id (str): The `thread_id` parameter is a unique identifier for the chat session. It is used
    to keep track of different chat sessions and their associated data.
    """
    
    chat_sessions[thread_id] = {
        "chatbot": create_chatBot_app(),
        "config": {"configurable": {"thread_id": thread_id}}
    }



@app.get("/sessions")
def list_sessions():
    """the function lists of active session IDs

    Returns:
        JSON: A dictionary is being returned with the key "active_sessions" and a list of thread IDs as the
    value.
    """    
    return {"active_sessions": [thread_id for thread_id in chat_sessions.keys()]}


@app.delete("/chat/delete/{thread_id}", status_code=status.HTTP_200_OK)
async def delete_session(thread_id: str):
    """
    Delete a chat session and its associated memory
    
    Parameters:
    - thread_id: The session identifier to delete
    
    Returns:
    - Message confirming deletion
    """
    try:
        if thread_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
            
        # Remove session from memory
        del chat_sessions[thread_id]
        
        return {
            "message": "Session deleted successfully",
            "thread_id": thread_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )


@app.post("/chat/start", response_model=ChatResponse)
async def start_new_chat():
    """starts a new chat session returns a greeting message along
    with a unique thread ID.

    Returns:
        response_model (ChatResponse): returning a JSON response with two keys: "answer" and "thread_id".
    """    
    thread_id = str(uuid.uuid4())
    initialize_chat_session(thread_id)
    return {
        "answer": "سلام! من یک ربات پزشکی هستم. چگونه می توانم به شما کمک کنم؟",
        "thread_id": thread_id
    }

@app.post("/chat/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """handles chat requests by processing user input through a chatbot and returning the
    response.

    Args:
        request (ChatRequest): contains information such as the thread ID and the user's prompt.

    Returns:
        resoponse_model (ChatResponse): a dictionary containing the answer to the user's question and the thread ID.
    """    
    try:
        # Validate thread ID
        if request.thread_id and request.thread_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Invalid thread ID")
        
        # Create new session if no thread ID provided
        if not request.thread_id:
            return await start_new_chat()
            
        # Get session components
        session = chat_sessions[request.thread_id]
        chatbot = session["chatbot"]
        config = session["config"]
        
        # Validate input
        user_input = request.prompt.strip()
        if not user_input:
            raise HTTPException(status_code=400, detail="Empty prompt received")
        
        # Process input through LangGraph
        result = chatbot.invoke(
            {"user_question": user_input},
            config
        )
        
        return {
            "answer": result['answer_to_user_questoin'],
            "thread_id": request.thread_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)