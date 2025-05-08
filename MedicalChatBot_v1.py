
from rich import print as print_rich

from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings

from langchain_openai.chat_models.base import ChatOpenAI

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import Sequence
from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel, Field

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"


# step 1: load vectorDB of a dataset
embedding_jina3 = HuggingFaceEmbeddings(
                            model_name="jinaai/jina-embeddings-v3",
                            model_kwargs={'device': device, 'trust_remote_code': True},
                            encode_kwargs={'normalize_embeddings': False}
                            )

vectorDB_faiss_drugQA = FAISS.load_local('faissDB_Collection',\
    embeddings=embedding_jina3, index_name='darooyab_qa_train', allow_dangerous_deserialization=True)


# step 2: load llm from ollama with openai api
openai_api_key = 'ollama'
BASE_URL = 'http://ollama-gpu:11434/v1/'
openai_kwargs = {'openai_api_key': openai_api_key,
                 'base_url': BASE_URL,
                 'max_tokens': 500,
                #  uncomment the model that you can run
                 'model': 'hf.co/bartowski/aya-expanse-8b-GGUF:Q6_K_L', # main model
                #  'model': 'hf.co/bartowski/gemma-2-2b-it-GGUF:Q6_K_L', # smaller model for run on personal pc
                 'temperature': 0.1}

chat_model = ChatOpenAI(**openai_kwargs)



# step 3: langgraph workflow
def create_chatBot_app ():
    
    promptTemplate_system = """
    You are a helpful Persian medical question answering chatbot.
    Please answer the questions in the asked language.
    """

    promptTemplate_rag = """
    user input: {user_question}\n\n\n
    consider this context:\n
    {context}\n\n\n
    just answer user question, not even a word more.
    """

    promptTemplate_rag = PromptTemplate.from_template(promptTemplate_rag)


    chatPromptTemplate = ChatPromptTemplate([
        ("system", promptTemplate_system),
        ("placeholder", "{conversation}"), # or use: MessagesPlaceholder(variable_name="conversation", optional=True)
        ])

    class OutputStructure_is_rag(BaseModel):
        is_rag: str = Field(description="identify whether we need rag or not?", enum=["yes", "no"])

    class State(TypedDict):
        user_question: str
        context: str
        answer_to_user_questoin: str
        conversation: Annotated[Sequence[BaseMessage], add_messages]

    def add_userQuestion_to_conversation(state: State):
        return {"conversation": [("human", state["user_question"])]}


    def retrieve(state: State):

        retrived_QA = vectorDB_faiss_drugQA.similarity_search(state["user_question"], k=1)
        question = retrived_QA[0].page_content
        answer = retrived_QA[0].metadata["answer"]

        out_temp = chat_model.with_structured_output(OutputStructure_is_rag).invoke(f"tell whether the answer of this question: {state['user_question']},\
        is presented (yes) or not (no) in this text: {question + answer}")

        if out_temp.is_rag=="yes":
            return {"context": question + answer}
        return {"context": ""}



    def generate(state: State):
        prompt_rag = promptTemplate_rag.format(user_question=state["user_question"],
                                               context=state["context"],
                                               )
        prompt_chat = chatPromptTemplate.format(conversation=(state["conversation"][:-1]+[("human", prompt_rag)]))

        response = chat_model.invoke(prompt_chat)
        return {"answer_to_user_questoin": response.content,
                "conversation": [response]}


    chatBot_app_builder = StateGraph(state_schema=State).add_sequence([add_userQuestion_to_conversation, retrieve, generate])
    chatBot_app_builder.add_edge(START, "add_userQuestion_to_conversation")


    memory = MemorySaver()
    chatBot_app = chatBot_app_builder.compile(checkpointer=memory)
    
    return chatBot_app








if __name__=="__main__":
    chatBot_app = create_chatBot_app()
    
    # set arguments for invoke chatBot_app
    config_user = {"configurable": {"thread_id": "abc123"}}
    
    
    while True:
        # read user question and handle exit command (e)
        user_question = input("enter questoin (e for exit): ")
        if user_question.lower()=="e": break
        
        input_dict = {"user_question": f"{user_question}"}
        output = chatBot_app.invoke(input_dict, config_user)
        
        print_rich(output['answer_to_user_questoin'])
