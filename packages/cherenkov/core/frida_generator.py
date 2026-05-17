"""Frida Hook Generator - Produces JS hooks from CWE findings"""

from typing import Dict


class FridaHookGenerator:
    """Generates Frida JS snippets for dynamic instrumentation based on CWEs"""

    _TEMPLATES: Dict[str, str] = {
        "CWE-532": """
            // CWE-532: Insecure Log Exposure
            Java.perform(function() {
                var Log = Java.use("android.util.Log");
                Log.d.overload("java.lang.String", "java.lang.String").implementation = function(tag, msg) {
                    send({
                        type: "finding",
                        cwe: "CWE-532",
                        title: "Insecure Logging Detected",
                        evidence: "Tag: " + tag + " | Msg: " + msg,
                        severity: "MEDIUM"
                    });
                    return this.d(tag, msg);
                };
            });
        """,
        "CWE-922": """
            // CWE-922: Insecure Storage of Sensitive Information
            Java.perform(function() {
                var SharedPreferences = Java.use("android.app.SharedPreferencesImpl$EditorImpl");
                SharedPreferences.putString.implementation = function(key, value) {
                    send({
                        type: "finding",
                        cwe: "CWE-922",
                        title: "Sensitive Data Written to SharedPreferences",
                        evidence: "Key: " + key + " | Value: " + value,
                        severity: "HIGH"
                    });
                    return this.putString(key, value);
                };
            });
        """,
        "CWE-749": """
            // CWE-749: Exposed Dangerous Method or Function
            Java.perform(function() {
                var WebView = Java.use("android.webkit.WebView");
                WebView.addJavascriptInterface.implementation = function(obj, name) {
                    send({
                        type: "finding",
                        cwe: "CWE-749",
                        title: "Dangerous WebView Interface Exposed",
                        evidence: "Interface Name: " + name,
                        severity: "CRITICAL"
                    });
                    return this.addJavascriptInterface(obj, name);
                };
            });
        """,
    }

    @classmethod
    def generate(cls, cwe: str) -> str:
        """Returns a Frida JS hook for the given CWE, or a generic monitor if unknown."""
        return cls._TEMPLATES.get(
            cwe, f"// Generic monitor for {cwe}\nconsole.log('Monitoring {cwe}...');"
        )

    @classmethod
    def list_supported_cwes(cls) -> list[str]:
        return list(cls._TEMPLATES.keys())
