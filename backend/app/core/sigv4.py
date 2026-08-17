"""AWS SigV4 authentication flow for httpx requests."""
import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


class SigV4HttpxAuth(httpx.Auth):
    """httpx Auth flow that signs every request with AWS SigV4."""

    requires_request_body = True

    def __init__(self, credentials, service: str, region: str):
        self.credentials = credentials
        self.service = service
        self.region = region

    def auth_flow(self, request: httpx.Request):
        body = request.read()

        aws_request = AWSRequest(
            method=request.method,
            url=str(request.url),
            data=body,
            headers=dict(request.headers),
        )

        SigV4Auth(self.credentials, self.service, self.region).add_auth(aws_request)

        for header_key, header_val in aws_request.headers.items():
            request.headers[header_key] = header_val

        yield request
