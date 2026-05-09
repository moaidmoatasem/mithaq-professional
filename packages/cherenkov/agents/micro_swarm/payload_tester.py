from typing import Any, Dict


class PayloadTester:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def test(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "passed", "payload": payload}
