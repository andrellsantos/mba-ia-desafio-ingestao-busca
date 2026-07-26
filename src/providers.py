import os

from dotenv import load_dotenv

load_dotenv()


def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai").strip().lower()


def get_embeddings():
    if _provider() == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
        )

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )


def get_llm():
    if _provider() == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_CHAT_MODEL", "gemini-2.5-flash-lite"),
            temperature=0,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano"),
    )
