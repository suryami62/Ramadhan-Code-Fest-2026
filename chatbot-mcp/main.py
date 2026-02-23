from fastmcp import FastMCP
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

sql = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

mcp = FastMCP("sql-mcp")
db = chromadb.PersistentClient(path="./faq_db")
collection = db.get_or_create_collection(name="faq_docs")


@mcp.prompt()
def system_prompt():
    return """
    You are a SQL expert assistant.
    Use the available tools to answer questions about the database.
    ## Rules you MUST follow:
    1. **Forbidden Query**: You are STRICTLY PROHIBITED from executing any DELETE query.
       Only SELECT, INSERT, and UPDATE queries are allowed.
       If the user requests a deletion, politely refuse and suggest an alternative
       (e.g., using a soft-delete flag with UPDATE, or inform the user that DELETE is not permitted).
    2. **Confirmation Before Data Changes**: Before executing any INSERT or UPDATE query,
       you MUST first show the query to the user and ask for their confirmation.
       Only proceed with the execution after the user explicitly approves it.
       Example confirmation message:
       "I'm about to run the following query:
       [query here]
       Do you confirm? (yes/no)"
    """


@mcp.tool()
def execute_query(query: str) -> str:
    """
    Execute a SQL query and return the results
    """
    query_upper = query.strip().upper()

    if query_upper.startswith("DELETE"):
        return "Delete is not allowed"

    try:
        with sql.connect() as conn:
            result = conn.execute(text(query))

            # SELECT: kembalikan hasil rows
            if query_upper.startswith("SELECT"):
                rows = result.fetchall()
                if rows:
                    return str(rows)
                else:
                    return "No results"

            # INSERT / UPDATE: commit agar tersimpan ke DB
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {result.rowcount}"

    except Exception as e:
        return str(e)


@mcp.tool()
def save_faq_docs(question: str, answer: str) -> str:
    """
    Query from database to get faq docs and save to local vector database
    """
    data = []
    query = execute_query("SELECT question, answer FROM faq")
    data.append({"question": query[0], "answer": query[1]})

    vector = SentenceTransformer("all-MiniLM-L6-v2")
    embed_data = vector.encode(data)
    collection.upsert(
        documents=[doc["question"] for doc in data],
        metadatas=[doc["answer"] for doc in data],
        ids=[str(i) for i in range(len(embed_data))],
        embeddings=embed_data,
    )

    return "FAQ docs saved to vector database"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=5000)
