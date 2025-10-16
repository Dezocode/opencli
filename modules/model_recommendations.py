"""
Local Model Recommendations for Code Editing

Based on system capabilities and model performance characteristics.
Focuses on models optimized for code editing, refactoring, and tool calls.
"""

from typing import Dict, List


# Model recommendation database
# Based on extensive testing for Claude Code-style editing workflows
MODEL_RECOMMENDATIONS = {
    "red": {
        "tier_name": "Basic (8-16GB)",
        "description": "Optimized for snappy response on modest hardware",
        "single_model": {
            "primary": {
                "name": "qwen2.5-coder:7b",
                "full_name": "Qwen2.5-Coder-7B-Instruct",
                "size": "7B",
                "quantization": "q4",
                "purpose": "All-in-one coder",
                "speed": "15-30 tok/s",
                "context": "32k tokens",
                "why": "Best-in-class 7B coder. Strong instruction-following, stable JSON tool calls, excellent edit diffs.",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 16384,
                    "repeat_penalty": 1.05
                }
            },
            "alternative": {
                "name": "deepseek-coder-v2.5:7b",
                "full_name": "DeepSeek-Coder-V2.5-7B",
                "size": "7B",
                "quantization": "q4",
                "purpose": "Algorithmic tasks",
                "speed": "15-30 tok/s",
                "context": "16k tokens",
                "why": "Punchier on algorithms, slightly looser on JSON discipline.",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 16384,
                    "repeat_penalty": 1.05
                }
            }
        },
        "dual_model": {
            "planner": {
                "name": "deepseek-r1:7b",
                "full_name": "DeepSeek-R1-Distill-7B",
                "size": "7B",
                "quantization": "q4",
                "purpose": "Planning & validation",
                "speed": "15-25 tok/s",
                "why": "Excellent at task decomposition and validation",
                "settings": {
                    "temperature": 0.2,
                    "num_ctx": 16384,
                    "repeat_penalty": 1.03
                }
            },
            "coder": {
                "name": "qwen2.5-coder:7b",
                "full_name": "Qwen2.5-Coder-7B-Instruct",
                "size": "7B",
                "quantization": "q4",
                "purpose": "Precise edits",
                "speed": "15-30 tok/s",
                "why": "Steady at minimal, correct diffs",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 16384,
                    "repeat_penalty": 1.05
                }
            }
        },
        "warnings": [
            "Do NOT try 14B models - will thrash memory",
            "Keep other apps closed during sessions",
            "Consider single-model for simplicity"
        ]
    },
    "yellow": {
        "tier_name": "Medium (18-36GB)",
        "description": "Sweet spot for serious refactoring work",
        "single_model": {
            "primary": {
                "name": "qwen2.5-coder:14b",
                "full_name": "Qwen2.5-Coder-14B-Instruct",
                "size": "14B",
                "quantization": "q4",
                "purpose": "All-in-one coder",
                "speed": "8-18 tok/s",
                "context": "32k tokens",
                "why": "Noticeable jump in reliability for large refactors and multi-file reasoning. Still fast enough for interactive editing.",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 32768,
                    "repeat_penalty": 1.05
                }
            }
        },
        "dual_model": {
            "planner": {
                "name": "deepseek-r1:14b",
                "full_name": "DeepSeek-R1-Distill-Qwen-14B",
                "size": "14B",
                "quantization": "q4",
                "purpose": "Planning & validation",
                "speed": "8-16 tok/s",
                "why": "Excellent at planning and validating diffs. Strong task decomposition.",
                "settings": {
                    "temperature": 0.2,
                    "num_ctx": 32768,
                    "repeat_penalty": 1.03
                }
            },
            "coder": {
                "name": "qwen2.5-coder:14b",
                "full_name": "Qwen2.5-Coder-14B-Instruct",
                "size": "14B",
                "quantization": "q4",
                "purpose": "Precise edits",
                "speed": "8-18 tok/s",
                "why": "Steadier at precise code edits with great diff quality",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 32768,
                    "repeat_penalty": 1.05
                }
            }
        },
        "recommended_approach": "dual_model",
        "why_dual": "Closest local feel to Claude Code's plan-then-edit behavior at this tier",
        "warnings": [
            "14B models are the sweet spot here",
            "Dual-model setup recommended for complex refactors",
            "Can push num_ctx to 32k without issues"
        ]
    },
    "green": {
        "tier_name": "High (36GB+)",
        "description": "Elite local setup - maximum quality",
        "single_model": {
            "primary": {
                "name": "qwen2.5-coder:32b",
                "full_name": "Qwen2.5-Coder-32B-Instruct",
                "size": "32B",
                "quantization": "q4",
                "purpose": "Heavy-duty coder",
                "speed": "4-10 tok/s",
                "context": "32k tokens",
                "why": "Best 'local big-gun coder' available. Exceptional quality for complex refactors.",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 32768,
                    "repeat_penalty": 1.05
                }
            }
        },
        "dual_model": {
            "planner": {
                "name": "deepseek-r1:32b",
                "full_name": "DeepSeek-R1-Distill-Qwen-32B",
                "size": "32B",
                "quantization": "q4",
                "purpose": "Elite planning",
                "speed": "4-10 tok/s",
                "why": "Closest to Claude Code's planning quality locally available",
                "settings": {
                    "temperature": 0.2,
                    "num_ctx": 32768,
                    "repeat_penalty": 1.03
                }
            },
            "coder": {
                "name": "qwen2.5-coder:32b",
                "full_name": "Qwen2.5-Coder-32B-Instruct",
                "size": "32B",
                "quantization": "q4",
                "purpose": "Maximal edit quality",
                "speed": "4-10 tok/s",
                "why": "Highest quality edits with excellent diff precision",
                "settings": {
                    "temperature": 0.15,
                    "num_ctx": 32768,
                    "repeat_penalty": 1.05
                }
            }
        },
        "hybrid_option": {
            "description": "Balanced speed + quality",
            "planner": {
                "name": "deepseek-r1:14b",
                "size": "14B",
                "why": "Snappier plans with 14B, still excellent quality"
            },
            "coder": {
                "name": "qwen2.5-coder:32b",
                "size": "32B",
                "why": "Keep maximal edit quality where it matters"
            }
        },
        "recommended_approach": "dual_model",
        "why_dual": "This is the closest local experience to Claude Code's autonomous editing",
        "warnings": [
            "32B will be slower - expect 4-10 tok/s",
            "Consider hybrid (planner@14B + coder@32B) for speed",
            "Keep num_ctx at 32k for best repo-scale reasoning"
        ]
    }
}


def get_recommendations(tier: str, is_apple_silicon: bool = False) -> Dict:
    """
    Get model recommendations for a capability tier

    Args:
        tier: "red", "yellow", or "green"
        is_apple_silicon: Whether running on Apple Silicon

    Returns:
        Dictionary with recommendations
    """
    base_recs = MODEL_RECOMMENDATIONS.get(tier, MODEL_RECOMMENDATIONS["red"])

    # Add Apple Silicon specific notes
    if is_apple_silicon:
        base_recs["platform_notes"] = (
            "Apple Silicon (M-series) benefits:\n"
            "  • Unified memory architecture\n"
            "  • Excellent Metal acceleration\n"
            "  • Can push higher num_ctx than specs suggest"
        )

    return base_recs


def format_recommendation_text(recs: Dict, show_dual: bool = True) -> str:
    """
    Format recommendations as readable text for CLI display

    Args:
        recs: Recommendations dict from get_recommendations()
        show_dual: Whether to show dual-model recommendations

    Returns:
        Formatted text for display
    """
    lines = []

    # Header
    lines.append(f"\n▸ {recs['tier_name']}: {recs['description']}\n")

    # Single model recommendation
    lines.append("PRIMARY RECOMMENDATION:")
    primary = recs["single_model"]["primary"]
    lines.append(f"  {primary['name']}")
    lines.append(f"  Size: {primary['size']} ({primary['quantization']})")
    lines.append(f"  Speed: {primary['speed']} on Apple Silicon")
    lines.append(f"  Why: {primary['why']}\n")

    # Dual model if requested and available
    if show_dual and "dual_model" in recs:
        lines.append("DUAL-MODEL SETUP (recommended for complex work):")
        planner = recs["dual_model"]["planner"]
        coder = recs["dual_model"]["coder"]

        lines.append(f"  Planner: {planner['name']} ({planner['size']})")
        lines.append(f"    → {planner['why']}")
        lines.append(f"  Coder: {coder['name']} ({coder['size']})")
        lines.append(f"    → {coder['why']}\n")

        if "why_dual" in recs:
            lines.append(f"  Why dual: {recs['why_dual']}\n")

    # Warnings
    if "warnings" in recs:
        lines.append("IMPORTANT NOTES:")
        for warning in recs["warnings"]:
            lines.append(f"  • {warning}")

    # Platform-specific notes
    if "platform_notes" in recs:
        lines.append(f"\n{recs['platform_notes']}")

    return "\n".join(lines)


def get_ollama_pull_commands(recs: Dict, dual: bool = False) -> List[str]:
    """
    Generate ollama pull commands for recommended models

    Args:
        recs: Recommendations dict
        dual: Whether to pull dual-model setup

    Returns:
        List of ollama pull commands
    """
    commands = []

    # Always include primary
    primary = recs["single_model"]["primary"]
    commands.append(f"ollama pull {primary['name']}")

    # Add dual models if requested
    if dual and "dual_model" in recs:
        planner = recs["dual_model"]["planner"]["name"]
        coder = recs["dual_model"]["coder"]["name"]

        if planner not in [primary["name"]]:
            commands.append(f"ollama pull {planner}")
        if coder not in [primary["name"]]:
            commands.append(f"ollama pull {coder}")

    return commands
