"""
Performance monitoring and profiling utilities for ChosyTable
Provides real-time performance metrics and optimization insights
"""

import time
import functools
import logging
from typing import Dict, List, Callable, Any
from datetime import datetime, timedelta
from flask import request, g
from app import client

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Real-time performance monitoring and metrics collection"""
    
    def __init__(self, cache_client=None):
        self.cache = cache_client or client
        self.metrics_cache_ttl = 3600  # 1 hour
    
    def timing_decorator(self, operation_name: str):
        """Decorator to measure function execution time"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    # Log performance metric
                    self._record_metric(operation_name, execution_time, success, error)
                
                return result
            return wrapper
        return decorator
    
    def _record_metric(self, operation: str, execution_time: float, success: bool, error: str = None):
        """Record performance metric to cache and logs"""
        timestamp = datetime.now().isoformat()
        
        metric = {
            'operation': operation,
            'execution_time_ms': round(execution_time, 2),
            'timestamp': timestamp,
            'success': success,
            'error': error,
            'request_path': getattr(request, 'path', 'unknown') if request else 'background'
        }
        
        # Log metric
        if success:
            logger.info(f"PERF: {operation} completed in {execution_time:.2f}ms")
        else:
            logger.error(f"PERF: {operation} failed after {execution_time:.2f}ms - {error}")
        
        # Store in cache for metrics dashboard
        metrics_key = f"choosytable:metrics:{operation}"
        try:
            existing_metrics = self.cache.get(metrics_key) or []
            existing_metrics.append(metric)
            
            # Keep only last 100 metrics per operation
            if len(existing_metrics) > 100:
                existing_metrics = existing_metrics[-100:]
            
            self.cache.set(metrics_key, existing_metrics, self.metrics_cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache performance metric: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all monitored operations"""
        summary = {}
        
        # Common operations to check
        operations = [
            'get_user_reviews_optimized',
            'get_company_reviews_with_stats', 
            'get_interview_statistics_aggregated',
            'get_all_companies_optimized'
        ]
        
        for operation in operations:
            metrics_key = f"choosytable:metrics:{operation}"
            metrics = self.cache.get(metrics_key) or []
            
            if metrics:
                # Calculate statistics
                execution_times = [m['execution_time_ms'] for m in metrics if m['success']]
                success_count = sum(1 for m in metrics if m['success'])
                total_count = len(metrics)
                
                if execution_times:
                    summary[operation] = {
                        'avg_time_ms': round(sum(execution_times) / len(execution_times), 2),
                        'min_time_ms': round(min(execution_times), 2),
                        'max_time_ms': round(max(execution_times), 2),
                        'success_rate': round((success_count / total_count) * 100, 2),
                        'total_calls': total_count,
                        'last_24h': len([m for m in metrics 
                                       if (datetime.now() - datetime.fromisoformat(m['timestamp'])).days == 0])
                    }
        
        return summary
    
    def get_slow_operations(self, threshold_ms: float = 500) -> List[Dict]:
        """Get operations that exceeded the performance threshold"""
        slow_ops = []
        
        operations = [
            'get_user_reviews_optimized',
            'get_company_reviews_with_stats', 
            'get_interview_statistics_aggregated',
            'get_all_companies_optimized'
        ]
        
        for operation in operations:
            metrics_key = f"choosytable:metrics:{operation}"
            metrics = self.cache.get(metrics_key) or []
            
            for metric in metrics:
                if metric['execution_time_ms'] > threshold_ms:
                    slow_ops.append(metric)
        
        # Sort by execution time (slowest first)
        slow_ops.sort(key=lambda x: x['execution_time_ms'], reverse=True)
        
        return slow_ops[:20]  # Return top 20 slowest operations
    
    def clear_metrics(self, operation: str = None):
        """Clear performance metrics for specific operation or all operations"""
        if operation:
            metrics_key = f"choosytable:metrics:{operation}"
            self.cache.delete(metrics_key)
        else:
            # Clear all metrics (this is approximate - memcached doesn't support pattern deletion)
            operations = [
                'get_user_reviews_optimized',
                'get_company_reviews_with_stats', 
                'get_interview_statistics_aggregated',
                'get_all_companies_optimized'
            ]
            
            for op in operations:
                metrics_key = f"choosytable:metrics:{op}"
                self.cache.delete(metrics_key)

# Flask request timing middleware
def before_request():
    """Record request start time"""
    g.start_time = time.time()

def after_request(response):
    """Record request completion time"""
    if hasattr(g, 'start_time'):
        request_time = (time.time() - g.start_time) * 1000
        
        # Log slow requests
        if request_time > 1000:  # Requests slower than 1 second
            logger.warning(f"SLOW REQUEST: {request.path} took {request_time:.2f}ms")
        
        # Add performance header
        response.headers['X-Response-Time'] = f"{request_time:.2f}ms"
    
    return response

# Global performance monitor instance
perf_monitor = PerformanceMonitor()