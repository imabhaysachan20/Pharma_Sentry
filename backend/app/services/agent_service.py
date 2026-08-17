import os
import sys
import logging
import httpx
import boto3
from backend.app.core.config import settings

logger = logging.getLogger("PharmaSentryBackend")

# Add PharmaSentryAgent to Python module path for Strands imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
agent_pkg_path = os.path.join(PROJECT_ROOT, "pharmasentry", "app", "PharmaSentryAgent")
if agent_pkg_path not in sys.path:
    sys.path.append(agent_pkg_path)

def _get_runtime_sigv4_auth():
    from mcp_client.streamable_http_sigv4 import SigV4HttpxAuth
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            return None
        frozen = credentials.get_frozen_credentials()
        if frozen is None:
            return None
        region = session.region_name or settings.AWS_REGION
        return SigV4HttpxAuth(frozen, service="bedrock-agentcore", region=region)
    except Exception as e:
        logger.warning(f"Could not load AWS credentials for SigV4 signing: {e}")
        return None


async def detect_runtime_url() -> str:
    url = os.getenv("AGENTCORE_RUNTIME_URL")
    if url:
        return url
    # Scan local ports 8080-8083 for an active local AgentCore runtime (which responds with 200 OK to /ping)
    for port in [8082, 8080, 8081, 8083]:
        test_url = f"http://localhost:{port}/ping"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(test_url, timeout=0.5)
                if res.status_code == 200:
                    logger.info(f"Detected local AgentCore runtime/proxy on port {port}")
                    return f"http://localhost:{port}/invocations"
        except Exception:
            continue
    logger.info("Using deployed AWS AgentCore Runtime URL")
    return settings.DEPLOYED_RUNTIME_URL

async def stream_agent(prompt: str, session_id: str, correlation_id: str, user_id: str):
    url = await detect_runtime_url()
    headers = {
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
        "X-Amzn-Bedrock-AgentCore-Runtime-Request-Id": correlation_id,
        "X-Amzn-Bedrock-AgentCore-Runtime-Custom-User-Id": str(user_id),
        "X-Agentcore-Local": "true",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}

    logger.info(f"Piping request to AgentCore ({url}). Session: {session_id}, Request-Id: {correlation_id}, User: {user_id}")

    if url.startswith("http://localhost") or url.startswith("http://127.0.0.1"):
        auth = None
    else:
        auth = _get_runtime_sigv4_auth()

    async with httpx.AsyncClient(auth=auth) as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers, timeout=60.0) as response:
                if response.status_code != 200:
                    yield f"event: error\ndata: Failed to invoke agent: HTTP {response.status_code}\n\n"
                    return

                async for chunk in response.aiter_text():
                    yield chunk
        except Exception as e:
            logger.error(f"Error communicating with AgentCore Runtime: {str(e)}")
            yield f"event: error\ndata: Connection error: {str(e)}\n\n"
