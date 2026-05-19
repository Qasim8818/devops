"""
Core monitoring engine - Async real-time infrastructure monitoring
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
import httpx

from backend.logger import setup_logging
from backend.config import get_settings


logger = setup_logging()
settings = get_settings()


class MonitoringEngine:
    """Async monitoring engine with Prometheus integration"""
    
    def __init__(self, settings):
        self.settings = settings
        self.prometheus_url = settings.PROMETHEUS_URL
        self.monitor_interval = settings.MONITOR_INTERVAL
        self.is_running = False
        self.task = None
        self.anomalies: List[Dict[str, Any]] = []
        
    async def start(self):
        """Start monitoring loop"""
        self.is_running = True
        self.task = asyncio.create_task(self._monitoring_loop())
        logger.info("✅ Monitoring engine started")
        
    async def stop(self):
        """Stop monitoring loop"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Monitoring engine stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                await asyncio.sleep(self.monitor_interval)
                
                # Fetch metrics from Prometheus
                metrics = await self._fetch_prometheus_metrics()
                
                # Analyze for anomalies
                anomalies = await self._analyze_metrics(metrics)
                
                if anomalies:
                    self.anomalies = anomalies
                    logger.warning(f"🚨 Detected {len(anomalies)} anomalies")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}", exc_info=True)
                await asyncio.sleep(5)  # Retry after 5s
    
    async def _fetch_prometheus_metrics(self) -> Dict[str, Any]:
        """Fetch metrics from Prometheus"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Query Prometheus for key metrics
                queries = {
                    "container_cpu": 'rate(container_cpu_usage_seconds_total[1m]) * 100',
                    "container_memory": 'container_memory_usage_bytes / 1024 / 1024',
                    "http_requests_total": 'rate(http_requests_total[5m])',
                    "http_errors_total": 'rate(http_requests_total{status=~"5.."}[5m])',
                }
                
                metrics = {}
                for metric_name, query in queries.items():
                    try:
                        response = await client.get(
                            f"{self.prometheus_url}/api/v1/query",
                            params={"query": query},
                            timeout=5.0,
                        )
                        data = response.json()
                        if data.get("status") == "success":
                            metrics[metric_name] = data.get("data", {})
                    except Exception as e:
                        logger.warning(f"Failed to fetch {metric_name}: {e}")
                        
                return metrics
                
        except Exception as e:
            logger.error(f"Prometheus fetch failed: {str(e)}")
            return {}
    
    async def _analyze_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze metrics for anomalies (rule-based)"""
        anomalies = []
        
        if not metrics:
            return anomalies
        
        # CPU anomaly detection
        cpu_data = metrics.get("container_cpu", {}).get("result", [])
        for result in cpu_data:
            try:
                value = float(result.get("value", [None, "0"])[1])
                if value > 80:  # CPU > 80%
                    anomalies.append({
                        "metric": "container_cpu",
                        "container": result.get("metric", {}).get("container_label_org_opencontainers_image_title"),
                        "value": value,
                        "threshold": 80,
                        "severity": "high" if value > 95 else "medium",
                        "description": f"CPU usage {value:.1f}% exceeds threshold",
                    })
            except (ValueError, IndexError):
                pass
        
        # Memory anomaly detection
        memory_data = metrics.get("container_memory", {}).get("result", [])
        for result in memory_data:
            try:
                value = float(result.get("value", [None, "0"])[1])
                if value > 2048:  # Memory > 2GB
                    anomalies.append({
                        "metric": "container_memory",
                        "container": result.get("metric", {}).get("container_label_org_opencontainers_image_title"),
                        "value": value,
                        "threshold": 2048,
                        "severity": "medium",
                        "description": f"Memory usage {value:.1f}MB exceeds threshold",
                    })
            except (ValueError, IndexError):
                pass
        
        # HTTP error rate anomaly
        error_data = metrics.get("http_errors_total", {}).get("result", [])
        for result in error_data:
            try:
                value = float(result.get("value", [None, "0"])[1])
                if value > 10:  # >10 errors/sec
                    anomalies.append({
                        "metric": "http_errors",
                        "service": result.get("metric", {}).get("job"),
                        "value": value,
                        "threshold": 10,
                        "severity": "high",
                        "description": f"Error rate {value:.1f} errors/sec exceeds threshold",
                    })
            except (ValueError, IndexError):
                pass
        
        return anomalies
    
    async def get_single_metric(self, metric_name: str) -> Dict[str, Any]:
        """Get a single metric from Prometheus"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": metric_name},
                )
                return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Failed to get metric {metric_name}: {e}")
            return {}
    
    async def get_recent_anomalies(self, minutes: int = 30) -> List[Dict[str, Any]]:
        """Get anomalies from the last N minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [a for a in self.anomalies if a.get("detected_at", datetime.utcnow()) > cutoff]
