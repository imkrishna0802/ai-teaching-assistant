from rag_chain import load_rag_chain

chain = load_rag_chain()

def get_chatbot_response(user_input: str) -> str:
    response = chain(user_input)

    if isinstance(response, dict):
        return response.get("result") or response.get("answer") or response.get("output") or str(response)

    if hasattr(response, "content"):
        return response.content

    return str(response)