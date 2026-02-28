import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Extract text from PDF
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(BytesIO(pdf.read()))
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

# Convert chunks into vectors
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Develop bot
def get_conversational_chain():
    prompt_template = """ANALYZE THE PDF CONTEXT and
    Answer the question as detailed as possible from the provided context.
    Context: \n{context}\n
    Question: \n{question}\n
    Answer:"""
    
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

# User input interface
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
    db = FAISS.load_local('faiss_index', embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    st.write("Bot's Response: ", response["output_text"])

# Streamlit app
def main():
    st.set_page_config(page_title="PDF Bot 📄")

    # CSS for dark mode with custom colors
    st.markdown("""
        <style>
        .stApp {
            background-color: black;
            color: white;
        }
        .stHeader{
            color: white;
        }
        .stTextInput > div > input {
            color: white;
        }
        .stFileUploader > div > div {
            background-color: black;
            color: white;
        }
        .stButton > button {
            background-color: black;
            color: white;
            border: none;
        }
        </style>
        """, unsafe_allow_html=True)

    st.header("PDF VOICE MATE BOT 📄")
    user_question = st.text_input("Ask any Question from the PDF Files")
    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Upload Your PDF Files:")
        pdf_docs = st.file_uploader("Click on the Submit & Process Button", accept_multiple_files=True, type='pdf')
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")

if __name__ == "__main__":
    main()