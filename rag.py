from data_processing import load_urls, load_text, split_documents
from embeddings import get_embeddings
from llm import get_llm
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
import os

def get_vectorstore():
    url_list = load_urls('data/urls.txt')
    loaded_texts = load_text(url_list)
    split_texts = split_documents(loaded_texts)

    print(f"✅ Number of documents loaded: {len(loaded_texts)}")
    print(f"✅ Number of split documents: {len(split_texts)}")

    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=split_texts,
        embedding=embeddings,
        persist_directory="db"
    )
    return vectorstore

def get_rag_chain(folder_path=None):
    vectorstore = get_vectorstore()
    llm = get_llm()

    # Promptul are nevoie de DOAR context și query
    prompt = PromptTemplate(
        input_variables=["context", "query"],
        template="""
        You are CyberAIAgent, a cybersecurity assistant specialized in code and configuration analysis.
        Your goal is to detect security vulnerabilities in the provided code snippet or configuration file, 
        based on best practices and known vulnerabilities (e.g., OWASP, CVE, CIS, SANS).

        Use the provided context (documentation and best practices) to analyze the user's input.

        -----
        Context:
        {context}

        -----
        Code or Configuration to Analyze:
        {question}

        -----
        Instructions:
        - Identify any security vulnerabilities, bad practices, or misconfigurations.
        - For each issue, include:
            1. A short name (e.g., "Hardcoded credentials", "Unpinned Docker tag")
            2. A clear explanation of why it's dangerous.
            3. A suggested fix or best practice.
        - If everything looks secure, say: "No major vulnerabilities detected."

        -----
        Answer:
        """
    )

    # Pas 1: LLMChain cu promptul tău
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Pas 2: StuffDocumentsChain care injectează contextul din vectorstore
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context"
    )

    # Pas 3: RetrievalQA complet, cu retriever + combine_documents_chain
    rag_chain = RetrievalQA(
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5}),
        combine_documents_chain=combine_documents_chain,
        return_source_documents=True
    )

    # Executare pe fișierele din folder
    if folder_path:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                code_content = file.read()
                context = vectorstore.similarity_search(code_content, k=5)
                result = rag_chain.invoke({"context": context, "query": code_content})
                print(f"\n📂 File: {file_path}")
                print("✅ Answer:\n", result['result'])

    return rag_chain

if __name__ == "__main__":
    folder_path = "data/code"
    get_rag_chain(folder_path=folder_path)