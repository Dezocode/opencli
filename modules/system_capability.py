"""
System Capability Detection for Local Model Recommendations

Privacy-first approach: Only collects minimal system info needed for
model recommendations. No data is sent anywhere - all processing is local.
"""

import platform
import os
import subprocess
from typing import Dict, Optional, Tuple


class SystemCapability:
    """Detects system capabilities for local model recommendations"""

    def __init__(self):
        self.os_type = platform.system()
        self.machine = platform.machine()
        self.os_version = platform.release()
        self._ram_gb = None
        self._vram_gb = None

    def detect_capabilities(self) -> Dict:
        """
        Detect system capabilities (RAM, GPU, CPU)

        Returns dict with:
        - os: Operating system name
        - arch: Architecture (arm64, x86_64, etc.)
        - ram_gb: Total RAM in GB
        - vram_gb: GPU VRAM in GB (if available)
        - gpu_type: GPU description
        - tier: "green"/"yellow"/"red" capability level
        """
        ram_gb = self._detect_ram()
        vram_gb, gpu_type = self._detect_gpu()

        tier = self._categorize_tier(ram_gb, vram_gb)

        return {
            "os": self.os_type,
            "arch": self.machine,
            "os_version": self.os_version,
            "ram_gb": ram_gb,
            "vram_gb": vram_gb,
            "gpu_type": gpu_type,
            "tier": tier,
            "is_apple_silicon": self._is_apple_silicon()
        }

    def _detect_ram(self) -> int:
        """Detect total system RAM in GB"""
        if self._ram_gb:
            return self._ram_gb

        try:
            if self.os_type == "Darwin":  # macOS
                # Use sysctl to get total RAM
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    bytes_ram = int(result.stdout.strip())
                    self._ram_gb = bytes_ram // (1024**3)
                    return self._ram_gb

            elif self.os_type == "Linux":
                # Read from /proc/meminfo
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb_ram = int(line.split()[1])
                            self._ram_gb = kb_ram // (1024**2)
                            return self._ram_gb

            elif self.os_type == "Windows":
                # Use wmic
                result = subprocess.run(
                    ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        bytes_ram = int(lines[1].strip())
                        self._ram_gb = bytes_ram // (1024**3)
                        return self._ram_gb

        except Exception:
            pass

        # Fallback: assume modest system
        return 8

    def _detect_gpu(self) -> Tuple[Optional[int], Optional[str]]:
        """
        Detect GPU VRAM and type

        Returns: (vram_gb, gpu_description)
        """
        if self._vram_gb and hasattr(self, '_gpu_type'):
            return self._vram_gb, self._gpu_type

        vram_gb = None
        gpu_type = None

        try:
            if self.os_type == "Darwin":  # macOS
                # Apple Silicon uses unified memory
                if self._is_apple_silicon():
                    # On Apple Silicon, GPU shares RAM
                    vram_gb = self._detect_ram()  # Unified memory

                    # Detect M-series chip
                    result = subprocess.run(
                        ["sysctl", "-n", "machdep.cpu.brand_string"],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        chip = result.stdout.strip()
                        if "Apple" in chip:
                            gpu_type = f"{chip} (Unified Memory)"
                        else:
                            gpu_type = "Apple Silicon"
                    else:
                        gpu_type = "Apple Silicon"
                else:
                    gpu_type = "Intel/AMD GPU"

            elif self.os_type == "Linux":
                # Try nvidia-smi for NVIDIA GPUs
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total,name", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    line = result.stdout.strip().split("\n")[0]
                    parts = line.split(",")
                    if len(parts) >= 2:
                        vram_mb = int(parts[0].strip())
                        vram_gb = vram_mb // 1024
                        gpu_type = parts[1].strip()

            elif self.os_type == "Windows":
                # Try nvidia-smi for NVIDIA GPUs
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total,name", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    line = result.stdout.strip().split("\n")[0]
                    parts = line.split(",")
                    if len(parts) >= 2:
                        vram_mb = int(parts[0].strip())
                        vram_gb = vram_mb // 1024
                        gpu_type = parts[1].strip()

        except Exception:
            pass

        self._vram_gb = vram_gb
        self._gpu_type = gpu_type
        return vram_gb, gpu_type

    def _is_apple_silicon(self) -> bool:
        """Check if running on Apple Silicon (M1/M2/M3/etc.)"""
        return self.os_type == "Darwin" and self.machine == "arm64"

    def _categorize_tier(self, ram_gb: int, vram_gb: Optional[int]) -> str:
        """
        Categorize system capability into green/yellow/red tier

        Based on unified memory (Apple Silicon) or RAM + VRAM:
        - Green: 36GB+ (can run 32B models smoothly)
        - Yellow: 18-35GB (can run 14B models comfortably)
        - Red: 8-17GB (stick to 7B models)
        """
        # For Apple Silicon, unified memory is the key metric
        if self._is_apple_silicon():
            effective_memory = ram_gb
        else:
            # For other systems, consider RAM + VRAM
            effective_memory = ram_gb + (vram_gb or 0)

        if effective_memory >= 36:
            return "green"
        elif effective_memory >= 18:
            return "yellow"
        else:
            return "red"

    def get_tier_description(self, tier: str) -> str:
        """Get human-readable description of capability tier"""
        descriptions = {
            "green": "High capability - Can run 32B models smoothly",
            "yellow": "Medium capability - Best with 14B models",
            "red": "Basic capability - Recommended 7B models"
        }
        return descriptions.get(tier, "Unknown tier")

    def get_privacy_notice(self) -> str:
        """Return privacy notice about what we detect"""
        return (
            "System capability detection is privacy-first:\n"
            "  • Only detects: RAM, GPU type, OS version\n"
            "  • All processing is local\n"
            "  • No data sent anywhere\n"
            "  • Used only for model recommendations"
        )
