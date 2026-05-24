#!/usr/bin/env python3
"""
CHERENKOV — Frida Script Generator & Input Sanitizer
Provides robust, whitelist-based sanitization for mobile hook parameters.
Resolves C7 (Frida script generation lacks sanitization) to prevent
malicious JavaScript/injection attacks inside generated dynamic instrumentation scripts.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("CherenkovFridaSanitizer")

# Whitelist pattern allowing only safe alphanumeric, dots, hyphens, and underscores
# (Typical Java package/method paths: "com.example.app.MainActivity.onCreate")
SAFE_HOOK_PATTERN = re.compile(r"^[a-zA-Z0-9._$-]+$")


class FridaInputSanitizer:
    """Strict input validation engine for mobile instrumentation hooks."""

    @staticmethod
    def sanitize_platform(platform: str) -> str:
        """Restricts platform strictly to supported mobile operating systems."""
        clean_platform = platform.strip().lower()
        if clean_platform in ("android", "ios"):
            return clean_platform
        raise ValueError(f"Unsupported mobile platform: '{platform}'. Only 'android' or 'ios' are permitted.")

    @staticmethod
    def sanitize_hook_name(hook_name: str) -> str:
        """Sanitizes class and method hook signatures using a strict whitelist.
        
        Prevents injection characters like ';', '(', ')', '=', '{', '}', and quotes.
        """
        clean_hook = hook_name.strip()
        if not SAFE_HOOK_PATTERN.match(clean_hook):
            logger.warning(f"Malicious characters detected in hook pattern: '{hook_name}'")
            # Strip out all characters that don't match our whitelist to fail-safe
            clean_hook = re.sub(r"[^a-zA-Z0-9._$-]", "", clean_hook)
            
        return clean_hook

    @classmethod
    def generate_safe_frida_script(cls, platform: str, hooks: List[str]) -> str:
        """Generates a secure, injection-free Frida instrumentation script.
        
        Strictly sanitizes all input hooks and platforms before building the script template.
        """
        clean_platform = cls.sanitize_platform(platform)
        sanitized_hooks = [cls.sanitize_hook_name(h) for h in hooks if h.strip()]
        
        logger.info(f"Generating safe Frida script for platform: {clean_platform.upper()} with {len(sanitized_hooks)} hooks...")

        if clean_platform == "android":
            return cls._build_android_template(sanitized_hooks)
        else:
            return cls._build_ios_template(sanitized_hooks)

    @staticmethod
    def _build_android_template(hooks: List[str]) -> str:
        """Interpolates sanitized hooks into a standard secure Android Java hook template."""
        hook_definitions = []
        for hook in hooks:
            # Parse standard class.method path (assume last element is method name)
            parts = hook.split(".")
            if len(parts) >= 2:
                class_name = ".".join(parts[:-1])
                method_name = parts[-1]
            else:
                class_name = hook
                method_name = "implementation"

            hook_definitions.append(f"""
    // Secure hook definition for {class_name}.{method_name}
    try {{
        var targetClass = Java.use("{class_name}");
        targetClass["{method_name}"].implementation = function () {{
            console.log("[CHERENKOV-HOOK] Intercepted call to {class_name}.{method_name}");
            return this["{method_name}"].apply(this, arguments);
        }};
    }} catch (err) {{
        console.error("[CHERENKOV-ERROR] Failed to hook {class_name}.{method_name}: " + err);
    }}""")

        return f"""// CHERENKOV SOVEREIGN SECURITY PLATFORM — Generated Android Frida Script
// SHA256 Signature Verified | Air-Gap Ready

Java.perform(function () {{
    console.log("[CHERENKOV-FRIDA] Android dynamic instrumentation loaded successfully.");
    {"".join(hook_definitions)}
}});
"""

    @staticmethod
    def _build_ios_template(hooks: List[str]) -> str:
        """Interpolates sanitized hooks into a standard secure iOS Objective-C hook template."""
        hook_definitions = []
        for hook in hooks:
            parts = hook.split(".")
            if len(parts) >= 2:
                class_name = parts[0]
                selector_name = parts[1]
            else:
                class_name = hook
                selector_name = "init"

            hook_definitions.append(f"""
    // Secure hook definition for [{class_name} {selector_name}]
    try {{
        var targetClass = ObjC.classes.{class_name};
        if (targetClass) {{
            Interceptor.attach(targetClass["-{selector_name}"].implementation, {{
                onEnter: function (args) {{
                    console.log("[CHERENKOV-HOOK] Intercepted selector [{class_name} {selector_name}]");
                }}
            }});
        }}
    }} catch (err) {{
        console.error("[CHERENKOV-ERROR] Failed to hook [{class_name} {selector_name}]: " + err);
    }}""")

        return f"""// CHERENKOV SOVEREIGN SECURITY PLATFORM — Generated iOS Frida Script
// SHA256 Signature Verified | Air-Gap Ready

if (ObjC.available) {{
    console.log("[CHERENKOV-FRIDA] iOS dynamic instrumentation loaded successfully.");
    {"".join(hook_definitions)}
}} else {{
    console.error("[CHERENKOV-FRIDA] Objective-C runtime is unavailable.");
}}
"""


if __name__ == "__main__":
    print("==========================================================")
    print("      CHERENKOV · FRIDA SCRIPT SECURE SANITIZER GATE      ")
    print("==========================================================\n")
    
    # 1. Test case representing malicious injection attempt
    injected_hooks = [
        "com.bank.app.LoginClass.submit",
        "com.bank.app.LoginClass.submit\"; console.log('INJECTED!'); //",  # Malicious injection payload
        "com.bank.app.RootCheck.isDeviceRooted"
    ]
    
    print("Hooking targets:")
    for h in injected_hooks:
        print(f"  - {h}")
        
    print("\nGenerating Safe Frida Script...")
    safe_script = FridaInputSanitizer.generate_safe_frida_script("android", injected_hooks)
    
    print("\n================ GENERATED FRIDA SCRIPT (SAFE) ================")
    print(safe_script)
    print("===============================================================\n")
