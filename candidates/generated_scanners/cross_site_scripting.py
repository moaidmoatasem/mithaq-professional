import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CrossSiteScriptingQueryParameterScanner(BaseScanner):
    """CWE-79: Cross-site scripting via reflected query parameters. Reflected XSS occurs when an application takes untrusted data and includes it in a new web page without proper validation or escaping, making it executable by other users. To mitigate this vulnerability, ensure that all user input is properly validated and encoded before being returned to the user.

    Tags: ['passive']
    """

    async def scan(self) -> ScanResult:
        results = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.target_url)
                if "Location" in response.headers:
                    redirect_url = response.headers["Location"]
                    params = httpx.urlparse(redirect_url).query
                    for key, value in httpx.parse_qs(params).items():
                        if any(char in value for char in "<>"):
                            results.append(
                                Finding(
                                    url=redirect_url,
                                    description=f"Potential Cross-site Scripting via reflected query parameter '{key}' with value '{value}'.",
                                    severity=Severity.MEDIUM,
                                )
                            )
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        return ScanResult(scanner=self.__class__.__name__, findings=results)
