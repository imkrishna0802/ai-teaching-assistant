from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import re

load_dotenv()

MAX_QUERY_LENGTH = 2000
_ALLOWED_QUERY_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _validate_query(query: str) -> str:
    """Sanitize and validate user query before passing to the vector store."""
    if not isinstance(query, str):
        raise ValueError("Query must be a string")
    query = query[:MAX_QUERY_LENGTH]
    query = _ALLOWED_QUERY_PATTERN.sub("", query)
    if not query.strip():
        raise ValueError("Query is empty after sanitization")
    return query



def load_rag_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )


    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )


    system_prompt = """You are a helpful AI teaching assistant for a programming course.
Your goal is to TEACH students, not just give them answers.


Use the following course material to answer the student's question.


Course material:
{context}


Student's Question:
{question}


Instructions:
- Explain concepts clearly and simply
- Use examples when helpful
- If the student seems stuck on code, give HINTS not complete solutions
- Encourage the student
- If the answer is not in the course material, say so honestly


Your Response:
"""


    def chain_fn(query: str) -> str:
        query = _validate_query(query)
        docs = vectorstore.similarity_search(query, k=3)
        context = "\n\n".join(d.page_content for d in docs)


        # build final prompt manually
        final_prompt = system_prompt.format(context=context, question=query)


        resp = llm.invoke(final_prompt)
        return resp.content if hasattr(resp, "content") else str(resp)


    return chain_fn