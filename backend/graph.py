from typing import Sequence
from typing_extensions import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages
from langgraph.graph import StateGraph, START, add_messages
from langgraph.checkpoint.memory import MemorySaver
from datetime import date


from backend.config import SYSTEM_PROMPT, MAX_TOKENS


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    persona: str
    language: str
    retrieved_context: str


def build_graph(model):
    # --- message trimmer (same as original logic) ---
    trimmer = trim_messages(
        max_tokens=MAX_TOKENS,
        strategy="last",
        token_counter=model,
        include_system=True,
        allow_partial=False,
        start_on="human"
    )

    # --- prompt template (WITH MessagesPlaceholder) ---
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ])

    def call_model(state: State):
        trimmed_messages = trimmer.invoke(state["messages"])

        prompt_input = {
            "messages": trimmed_messages,
            "persona": state["persona"],
            "language": state["language"],
            "retrieved_context": state.get("retrieved_context", ""),
            "today_date": date.today().isoformat(),
        }

        response = model.invoke(prompt.invoke(prompt_input))
        return {"messages": response}

    graph = StateGraph(State)
    graph.add_node("model", call_model)
    graph.add_edge(START, "model")

    return graph.compile(checkpointer=MemorySaver())
