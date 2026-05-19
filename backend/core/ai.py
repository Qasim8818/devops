"""
AI Engine - LLM-powered root cause analysis with rule-based fallback
"""

from typing import Dict, Any, Optional
import httpx
import json

from backend.logger import setup_logging
from backend.config import get_settings


logger = setup_logging()
settings = get_settings()


class AIEngine:
    """AI engine with Ollama integration and rule-based fallback"""
    
    def __init__(self, settings):
        self.settings = settings
        self.ollama_url = settings.OLLAMA_API_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.fallback_enabled = settings.LLM_FALLBACK_MODE
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama/LLM health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    return {"status": "healthy", "available_models": response.json()}
                else:
                    return {"status": "unhealthy", "error": "Invalid response"}
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def analyze_anomaly(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze anomaly using LLM with fallback"""
        
        prompt = self._build_analysis_prompt(anomaly)
        
        # Try LLM first
        if settings.OLLAMA_API_URL:
            try:
                llm_result = await self._call_ollama(prompt)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}")
                if not self.fallback_enabled:
                    raise
        
        # Fallback to rule-based analysis
        logger.info("Falling back to rule-based analysis")
        return self._rule_based_analysis(anomaly)
    
    async def _call_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Ollama LLM for analysis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.3,
                    },
                    timeout=float(self.timeout),
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    return self._parse_ollama_response(response_text)
                else:
                    logger.error(f"Ollama error: {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("Ollama request timeout")
            return None
        except Exception as e:
            logger.error(f"Ollama call failed: {str(e)}", exc_info=True)
            return None
    
    def _build_analysis_prompt(self, anomaly: Dict[str, Any]) -> str:
        """Build analysis prompt for LLM"""
        metric = anomaly.get("metric", "unknown")
        value = anomaly.get("value", 0)
        threshold = anomaly.get("threshold", 0)
        description = anomaly.get("description", "")
        
        prompt = f"""Analyze this infrastructure anomaly and provide root cause analysis and remediation steps:

Metric: {metric}
Current Value: {value}
Threshold: {threshold}
Description: {description}

Provide:
1. Root cause (1-2 sentences)
2. Severity (critical/high/medium/low)
3. Immediate actions (as a comma-separated list)
4. Long-term fix

Format your response as JSON with keys: root_cause, severity, immediate_actions, long_term_fix"""
        
        return prompt
    
    def _parse_ollama_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Ollama response"""
        try:
            # Try to extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        return self._rule_based_analysis({})
    
    def _rule_based_analysis(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback analysis"""
        metric = anomaly.get("metric", "unknown")
        
        # Predefined remediation rules
        rules = {
            "container_cpu": {
                "root_cause": "Container consuming excessive CPU",
                "severity": anomaly.get("severity", "high"),
                "immediate_actions": ["Scale horizontally", "Check for infinite loops", "Profile application"],
                "long_term_fix": "Optimize code and set resource limits",
            },
            "container_memory": {
                "root_cause": "Container memory leak or insufficient allocation",
                "severity": anomaly.get("severity", "medium"),
                "immediate_actions": ["Restart container", "Increase memory limit", "Check for leaks"],
                "long_term_fix": "Debug memory usage and implement proper cleanup",
            },
            "http_errors": {
                "root_cause": "Backend service experiencing errors",
                "severity": anomaly.get("severity", "high"),
                "immediate_actions": ["Check logs", "Verify database connectivity", "Check external APIs"],
                "long_term_fix": "Add better error handling and monitoring",
            },
        }
        
        return rules.get(metric, {
            "root_cause": "Unknown anomaly detected",
            "severity": "medium",
            "immediate_actions": ["Investigate manually", "Check recent deployments"],
            "long_term_fix": "Add specific monitoring rules for this metric",
        })
    
    async def generate_remediation_plan(
        self,
        anomaly: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate remediation plan"""
        
        return {
            "anomaly_id": anomaly.get("metric"),
            "analysis": analysis,
            "recommended_actions": analysis.get("immediate_actions", []),
            "auto_remediation_available": True,
            "requires_approval": analysis.get("severity") == "critical",
            "estimated_time": "2-5 minutes",
        }
