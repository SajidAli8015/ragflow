"""
backend/graph.py


Flow:
START ──► model

The graph:
- Maintains conversation state (messages + metadata)
- Trims message history to fit within a token budget
- Invokes the chat model once per turn
- Appends the model response back into the conversation state
"""

from typing import Sequence
from typing_extensions import TypedDict, Annotated
from datetime import date

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages

from langgraph.graph import StateGraph, START, add_messages
from langgraph.checkpoint.memory import MemorySaver

from backend.config import SYSTEM_PROMPT, MAX_TOKENS


# ---------------------------------------------------------------------
# Graph State Definition
# ---------------------------------------------------------------------
class State(TypedDict):
    """
    Defines the structure of the LangGraph state.

    - messages:
        Conversation history as LangChain message objects.
        Annotated with `add_messages` so LangGraph knows how to
        automatically append new messages returned by nodes.

    - persona:
        Optional metadata describing the assistant's persona.

    - language:
        Language in which the assistant should respond.

    - retrieved_context:
        Optional RAG context (can be empty if RAG is not used).
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    persona: str
    language: str
    retrieved_context: str


# ---------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------
def build_graph(model):
    """
    Builds and compiles the LangGraph.

    Args:
        model:
            A LangChain-compatible chat model instance
            (must support `.invoke()`).

    Returns:
        A compiled LangGraph runnable with memory checkpointing.
    """

    # -----------------------------------------------------------------
    # 1) Message Trimmer
    # -----------------------------------------------------------------
    # Ensures that conversation history stays within MAX_TOKENS.
    # Keeps the most recent messages and always preserves system messages.
    trimmer = trim_messages(
        max_tokens=MAX_TOKENS,
        strategy="last",          # Keep most recent messages
        token_counter=model,      # Use model's tokenizer for accuracy
        include_system=True,      # Preserve system prompt
        allow_partial=False,      # Do not keep partial messages
        start_on="human"          # Trim starting at human message boundary
    )

    # -----------------------------------------------------------------
    # 2) Prompt Template
    # -----------------------------------------------------------------
    # The prompt always includes:
    # - SYSTEM_PROMPT (system-level instructions)
    # - Conversation history via MessagesPlaceholder
    #
    # NOTE:
    # persona, language, retrieved_context, today_date will only be
    # used if SYSTEM_PROMPT contains placeholders like:
    # {persona}, {language}, {retrieved_context}, {today_date}
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
 
    # -----------------------------------------------------------------
    # 3) Graph Node: Call the Model
    # -----------------------------------------------------------------
    def call_model(state: State):
        """
        Graph node that:
        - Trims the message history
        - Formats the prompt
        - Invokes the chat model
        - Returns the model response to be appended to state
        """

        # Trim conversation messages to stay within token limits
        trimmed_messages = trimmer.invoke(state["messages"])

        # Inputs passed to the prompt template
        prompt_input = {
            "messages": trimmed_messages,
            "persona": state["persona"],
            "language": state["language"],
            "retrieved_context": state.get("retrieved_context", ""),
            "today_date": date.today().isoformat(),
        }

        # Step 1: Format prompt into messages
        formatted_prompt = prompt.invoke(prompt_input)

        # Step 2: Invoke the model with formatted messages
        response = model.invoke(formatted_prompt)

        # IMPORTANT:
        # Return messages as a list so LangGraph can safely append them
        return {"messages": [response]}

    # -----------------------------------------------------------------
    # 4) Define Graph Structure
    # -----------------------------------------------------------------
    graph = StateGraph(State)

    # Add the single model node
    graph.add_node("model", call_model)

    # Connect START → model
    graph.add_edge(START, "model")

    # -----------------------------------------------------------------
    # 5) Compile Graph with Memory
    # -----------------------------------------------------------------
    # MemorySaver enables state persistence between turns
    return graph.compile(checkpointer=MemorySaver())
