from datasets import load_dataset
from langchain_core.documents import Document
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

# step 1: load the dataset and clean it
drugQA = load_dataset("amirmmahdavikia/darooyab_qa", split="train")

def remove_rows_with_no_question(example):
  return example['question'] is not None

drugQA_removedRows_withNoQuestion = drugQA.filter(remove_rows_with_no_question)


# step 2: convert dataset to langchain document object
document_drugQA = [ Document(page_content=qa["question"], metadata={"answer": qa["answer"]})\
 for qa in drugQA_removedRows_withNoQuestion]


# step 3: create the vectorDB from embedding model
embedding_jina3 = HuggingFaceEmbeddings(
                            model_name="jinaai/jina-embeddings-v3",
                            model_kwargs={'device': device, 'trust_remote_code': True},
                            encode_kwargs={'normalize_embeddings': False}
                            )
vectorDB_faiss_drugQA = FAISS.from_documents(document_drugQA, embedding_jina3)


# step 4: save vectorDB
vectorDB_faiss_drugQA.save_local('faissDB_Collection', index_name='darooyab_qa_train')