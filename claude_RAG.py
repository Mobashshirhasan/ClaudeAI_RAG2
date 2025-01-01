import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain import hub

from langchain_anthropic import ChatAnthropic
import anthropic
from bs4 import BeautifulSoup

# Set your API keys
api_key = os.environ.get("ANTHROPIC_API_KEY")   
client = anthropic.Anthropic(api_key=api_key)

# Load the document from the web
loader = WebBaseLoader("https://onyxproerp.com/en/onyx-pro-erp/")
data = loader.load()

# Use OpenAI Embeddings for the document processing
embedding = OpenAIEmbeddings(model="text-embedding-3-large")

# Create a FAISS index and store the embeddings
faiss_db = FAISS.from_documents(documents=data, embedding=embedding)

# Persist the FAISS index to disk
faiss_db.save_local("./NEWfaiss_db")

# Load the FAISS index from the disk
faiss_db = FAISS.load_local(
    folder_path="./NEWfaiss_db",
    embeddings=embedding,
    allow_dangerous_deserialization=True    # Added this parameter
)

# Set up the LLM for Anthropic Claude
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
)

# Pull the prompt from the hub
prompt = hub.pull("rlm/rag-prompt")

# Set up the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=faiss_db.as_retriever(),
    chain_type_kwargs={"prompt": prompt},
)

# Ask a question
question = "What is onyx"
result = qa_chain({"query": question})

 # Print the result
print(result)
