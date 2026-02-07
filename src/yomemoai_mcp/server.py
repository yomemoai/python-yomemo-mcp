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
DEBUG = os.getenv("MEMO_DEBUG", "false").lower() == "true"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)

# Only write to log file in debug mode (MEMO_DEBUG=true)
if DEBUG:
    _log_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", ".."))
    _log_file = os.path.join(_log_dir, "yomemo-mcp.log")
    _file_handler = logging.FileHandler(_log_file)
    _file_handler.setLevel(LOG_LEVEL)
    _file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging.getLogger("yomemoai_mcp").addHandler(_file_handler)


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
                  Helps in contextual retrieval (PRT).use lowercase and no spaces.
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
            content, handle=handle, description=description, metadata=metadata)
        logger.debug(f"add_memory response: {result}")

        memory_id = result.get("memory_id")
        idempotent_key = result.get("idempotent_key")
        if not memory_id and result.get("data") and isinstance(result["data"], list) and len(result["data"]) > 0:
            first = result["data"][0]
            memory_id = first.get("id")
            idempotent_key = first.get("idempotent_key") or idempotent_key

        if not memory_id:
            resp_keys = list(result.keys()) if isinstance(
                result, dict) else type(result).__name__
            logger.error(
                "Failed to save memory for handle: %s, response keys: %s", handle, resp_keys)
            logger.info("save_memory response sample: %s", str(result)[:500])
            return f"Failed to save memory for handle: {handle}"

        return f"Successfully archived in memory. ID: {memory_id}, Idempotent Key: {idempotent_key or 'N/A'} "
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
async def load_memories(
    handle: Optional[str] = None,
    limit: int = 20,
    cursor: str = "",
    mode: str = "summary",
) -> str:
    """
    Retrieve previously stored memories with pagination and optional lightweight modes to reduce token usage.

    **Recommended flow to avoid token explosion:**
    1. Call first with mode='summary' (default) or mode='metadata' to get a lightweight list.
    2. From the list, decide whether to load the next page (use returned next_cursor) or load full content for the current set (call again with same cursor and mode='full').

    :param handle: Optional. Filter by category (e.g. 'work', 'project-x'). Omit to load across all handles.
    :param limit: Number of memories per page (default 20). Use with cursor for pagination.
    :param cursor: Pagination cursor from the previous response's "Next cursor" line. Leave empty for first page.
    :param mode: What to return:
      - "summary": Only description + metadata + id/handle/idempotent_key (no content). Best first step to scan and decide.
      - "metadata": Only id, handle, created_at, metadata (no description, no content). Smallest payload.
      - "full": Full content (decrypted). Use after you know you need details for this page; same cursor/limit as the summary page to get that page's full content.

    The response includes a "Next cursor" line when there are more results; pass it as cursor in the next call to get the next page.
    Each memory includes Idempotent Key for updating via save_memory with the same idempotent_key.
    """
    logger.debug("load_memories called: handle=%s limit=%s cursor=%s mode=%s",
                 handle, limit, cursor, mode)
    try:
        only_metadata = mode == "metadata"
        only_summary = mode == "summary"
        if mode not in ("summary", "metadata", "full"):
            return f"Invalid mode: {mode}. Use 'summary', 'metadata', or 'full'."

        memories, next_cursor = client.get_memories(
            handle=handle,
            limit=limit if limit > 0 else 20,
            cursor=cursor,
            only_metadata=only_metadata,
            only_summary=only_summary,
        )
        logger.debug("Retrieved %s memories, next_cursor=%s",
                     len(memories), bool(next_cursor))

        if not memories:
            msg = f"No memories found for handle: {handle if handle else 'all'}."
            if cursor:
                msg += " (Try without cursor for first page.)"
            return msg

        lines = ["### Retrieved Memories (mode=%s):" % mode]
        for m in memories:
            handle_value = m.get("handle", "")
            idempotent_key = m.get("idempotent_key") or "N/A"
            meta = m.get("metadata")
            meta_str = json.dumps(meta, ensure_ascii=False) if meta else "{}"
            created = m.get("created_at", "")
            block = [
                "Handle: [%s]" % handle_value,
                "Idempotent Key: %s" % idempotent_key,
                "Created: %s" % created,
                "Metadata: %s" % meta_str,
            ]
            if not only_metadata:
                block.append("Description: %s" % (m.get("description") or ""))
            if not only_metadata and not only_summary:
                block.append("Content: %s" % (m.get("content") or ""))
            lines.append("\n".join(block))
            lines.append("---")
        if next_cursor:
            lines.append("Next cursor (for next page): %s" % next_cursor)
        logger.info("Loaded %s memories (mode=%s)", len(memories), mode)
        return "\n".join(lines)
    except Exception as e:
        logger.error(
            "Error retrieving memories: %s: %s", type(e).__name__, str(e), exc_info=DEBUG
        )
        return "Error retrieving memories: %s" % str(e)


def run_with_debug(host: str = "127.0.0.1", port: int = 5678) -> None:
    """Run MCP server with debugpy so Cursor/VS Code can attach for breakpoint debugging."""
    try:
        import debugpy
    except ImportError:
        raise SystemExit(
            "debugpy not installed. Install with: uv add --dev debugpy"
        )
    debugpy.listen((host, port))
    print(
        f"Debugger listening on {host}:{port}. Attach from Cursor/VS Code.", file=sys.stderr)
    debugpy.wait_for_client()
    mcp.run()


if __name__ == "__main__":
    if os.getenv("MCP_DEBUG") == "1":
        run_with_debug()
    else:
        mcp.run()
