import asyncio
import json
import logging
import os
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP
from .client import MemoClient, MemoRequestError

if "--version" in sys.argv or "-version" in sys.argv:
    from importlib.metadata import version
    print(version("yomemoai-mcp"))
    sys.exit(0)

from dotenv import load_dotenv
load_dotenv()

# Configure logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

mcp = FastMCP("yomemoai")

API_KEY = os.getenv("MEMO_API_KEY", "")
PRIV_KEY_PATH = os.getenv("MEMO_PRIVATE_KEY_PATH", "private.pem")
BASE_URL = os.getenv("MEMO_BASE_URL", "https://api.yomemo.ai")

if not API_KEY:
    raise ValueError("MEMO_API_KEY environment variable is required")

if not os.path.exists(PRIV_KEY_PATH):
    raise FileNotFoundError(
        f"Private key file not found: {PRIV_KEY_PATH}. "
        f"Please set MEMO_PRIVATE_KEY_PATH environment variable or place your private key at {PRIV_KEY_PATH}"
    )

try:
    with open(PRIV_KEY_PATH, "r") as f:
        private_pem = f.read()
except Exception as e:
    raise IOError(f"Failed to read private key from {PRIV_KEY_PATH}: {e}")

if not private_pem.strip():
    raise ValueError(f"Private key file {PRIV_KEY_PATH} is empty")

client = MemoClient(API_KEY, private_pem, BASE_URL)


def _format_payload(payload: dict) -> dict:
    if not payload:
        return {}
    return dict(payload)


@mcp.tool()
async def save_memory(content: str, handle: str = "general", description: str = "", metadata: dict = {}) -> str:
    """
    Archives a high-density knowledge asset using the Semantic Fingerprint Protocol.
    Proactively triggered by the AMP (Autonomous Persistence Trigger) during 'Moments of Truth' 
    such as strategic decisions, fact updates, or logic finalization.

    :param content: The actual high-density factual information, decision logic, or SOP. 
                   Maintain context while stripping conversational noise.
    :param handle: Categorical routing based on Layer ID (L1-L5) or specific project Name. 
                  Helps in contextual retrieval (PRT).
    :param description: A brief, non-sensitive summary or high-level tag for safe indexing and search. 
                        STRICT CONSTRAINT: Must NOT contain specific transactional details, 
                        PII, or sensitive affairs to prevent information leakage.
    :param metadata: MANDATORY. Stores high-dimensional tag data under the 'semantic_fingerprint' key, 
                    including ELAP metrics, ontology mode, and engineering VCS status.
    """
    logger.debug(
        f"save_memory called: handle={handle}, description={description}, content_length={len(content)}")
    try:
        result = client.add_memory(
            content, handle=handle, description=description,metadata=metadata)
        logger.debug(f"add_memory response: {result}")

        if "memory_id" not in result:
            return f"Failed to save memory for handle: {handle}"

        memory_id = result.get('memory_id')

        return f"Successfully archived in memory. ID: {memory_id}"
    except MemoRequestError as e:
        logger.error(
            f"Error saving memory: {type(e).__name__}: {str(e)}", exc_info=DEBUG)
        request_info = {
            "url": e.url,
            "status_code": e.status_code,
            "response_text": e.response_text,
            "payload": _format_payload(e.payload),
            "handle": handle,
            "description": description,
            "content_length": len(content),
        }
        # only debug mode return the request_info
        if DEBUG:
            return json.dumps(request_info, ensure_ascii=False)
        return f"Failed to save your memory: {str(e)}"
    except Exception as e:
        logger.error(
            f"Error saving memory: {type(e).__name__}: {str(e)}", exc_info=DEBUG)
        return (
            f"Failed to save your memory: {str(e)},"
            f"handle: {handle},description: {description},content: {content}"
        )


@mcp.tool()
async def load_memories(handle: Optional[str] = None) -> str:
    """
    Retrieve previously stored memories. Call this when the user asks what you remember, or when you
    need historical context (preferences, past decisions, project details) to answer accurately.

    :param handle: Optional filter. If the user specifies a category (e.g., 'work', 'project-x'),
                   use the relevant handle; otherwise omit to load across handles.

    The output includes each memory's handle, idempotent key, and content so that callers can
    later use the same idempotent key with save_memory to update existing memories instead of
    creating duplicates.
    """
    logger.debug(f"load_memories called: handle={handle}")
    try:
        memories = client.get_memories(handle=handle)
        logger.debug(f"Retrieved {len(memories)} memories")

        if not memories:
            logger.info(
                f"No memories found for handle: {handle if handle else 'all'}")
            return f"No memories found under the handle: {handle if handle else 'all'}."

        output = ["### Retrieved Memories:"]
        for m in memories:
            handle_value = m.get("handle")
            idempotent_key = m.get("idempotent_key") or "N/A"
            content = m.get("content")
            metadata = m.get("metadata")
            output.append(
                "Handle: [{handle}]\nIdempotent Key: {key}\nContent: {content}\n---".format(
                    handle=handle_value,
                    key=idempotent_key,
                    content=content,
                    metadata=json.dumps(metadata, ensure_ascii=False) if metadata else "{}")
            )
        logger.info(f"Successfully loaded {len(memories)} memories")
        return "\n".join(output)
    except Exception as e:
        logger.error(
            f"Error retrieving memories: {type(e).__name__}: {str(e)}", exc_info=DEBUG)
        return f"Error retrieving memories: {str(e)}"

if __name__ == "__main__":
    mcp.run()
