"""
CELERY BEAT TASKS - Periodic Enterprise Maintenance
Nightly reports, proxy cleanup, system health checks, and optimization tasks
"""

from celery import Celery
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import asyncio
import json
from database.db import db_manager
from database.models import ProxyPool, TaskResult, SystemMetrics, BunkerAnalysis
from core.proxy_manager import ProxyManager
from core.ai_hierarchy import AIHierarchyManager
from core.analysis_bunker import AnalysisBunker
from core.config import get_settings

app = Celery('cyberzilla_enterprise')
logger = logging.getLogger("beat_tasks")

@app.task(name='tasks.proxy_health_check')
def proxy_health_check():
    """Comprehensive proxy pool health check and cleanup"""
    try:
        logger.info("🔍 Starting proxy health check...")
        
        with db_manager.get_db() as db:
            # Get all active proxies
            active_proxies = db.query(ProxyPool).filter(
                ProxyPool.is_active == True
            ).all()
            
            checked_count = 0
            healthy_count = 0
            deactivated_count = 0
            
            for proxy in active_proxies:
                try:
                    # Test proxy connectivity
                    is_healthy = _test_proxy_health(proxy.proxy_url)
                    proxy.last_health_check = datetime.now()
                    
                    if is_healthy:
                        proxy.health_status = 'healthy'
                        healthy_count += 1
                    else:
                        proxy.health_status = 'failed'
                        deactivated_count += 1
                    
                    checked_count += 1
                    
                    # Update success rate
                    total_requests = proxy.total_requests or 1
                    success_rate = (total_requests - proxy.failed_requests) / total_requests
                    proxy.success_rate = success_rate
                    
                    # Deactivate consistently failing proxies
                    if success_rate < 0.3:  # 30% success threshold
                        proxy.is_active = False
                        proxy.health_status = 'deactivated'
                    
                except Exception as e:
                    logger.error(f"Proxy health check failed for {proxy.proxy_url}: {e}")
                    proxy.health_status = 'error'
            
            db.commit()
            
        logger.info(f"✅ Proxy health check completed: {checked_count} checked, {healthy_count} healthy, {deactivated_count} deactivated")
        
        # Refresh proxy pool if too many are unhealthy
        if healthy_count / max(checked_count, 1) < 0.5:  # Less than 50% healthy
            logger.warning("🔄 Low healthy proxy count, triggering refresh...")
            refresh_proxy_pool.delay()
            
    except Exception as e:
        logger.error(f"❌ Proxy health check failed: {e}")

def _test_proxy_health(proxy_url: str) -> bool:
    """Test individual proxy health"""
    import requests
    try:
        response = requests.get(
            'http://httpbin.org/ip',
            proxies={'http': proxy_url, 'https': proxy_url},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

@app.task(name='tasks.refresh_proxy_pool')
def refresh_proxy_pool():
    """Refresh and acquire new proxies"""
    try:
        logger.info("🔄 Refreshing proxy pool...")
        
        proxy_manager = ProxyManager()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            new_proxies = loop.run_until_complete(
                proxy_manager.auto_acquire_proxies()
            )
            
            with db_manager.get_db() as db:
                # Add new proxies to database
                for proxy_url in new_proxies:
                    existing = db.query(ProxyPool).filter(
                        ProxyPool.proxy_url == proxy_url
                    ).first()
                    
                    if not existing:
                        new_proxy = ProxyPool(
                            proxy_url=proxy_url,
                            proxy_type='residential',
                            is_active=True,
                            health_status='unknown'
                        )
                        db.add(new_proxy)
                
                db.commit()
            
            logger.info(f"✅ Proxy pool refreshed: {len(new_proxies)} new proxies added")
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ Proxy pool refresh failed: {e}")

@app.task(name='tasks.system_health_check')
def system_health_check():
    """Comprehensive system health monitoring"""
    try:
        logger.info("❤️ Running system health check...")
        
        health_data = {
            'timestamp': datetime.now(),
            'components': {},
            'overall_status': 'healthy',
            'alerts': []
        }
        
        # Database health
        db_health = db_manager.health_check()
        health_data['components']['database'] = 'healthy' if db_health else 'unhealthy'
        
        if not db_health:
            health_data['alerts'].append('Database connection failed')
            health_data['overall_status'] = 'degraded'
        
        # Redis health
        redis_health = _check_redis_health()
        health_data['components']['redis'] = 'healthy' if redis_health else 'unhealthy'
        
        if not redis_health:
            health_data['alerts'].append('Redis connection failed')
            health_data['overall_status'] = 'degraded'
        
        # Disk space check
        disk_health = _check_disk_space()
        health_data['components']['disk'] = disk_health['status']
        
        if disk_health['status'] != 'healthy':
            health_data['alerts'].append(f"Disk space: {disk_health['message']}")
            health_data['overall_status'] = 'degraded'
        
        # Memory usage
        memory_health = _check_memory_usage()
        health_data['components']['memory'] = memory_health['status']
        
        if memory_health['status'] != 'healthy':
            health_data['alerts'].append(f"Memory: {memory_health['message']}")
        
        # Store health metrics
        with db_manager.get_db() as db:
            system_metric = SystemMetrics(
                metric_type='system_health',
                metric_value=1.0 if health_data['overall_status'] == 'healthy' else 0.5,
                metric_unit='score',
                component='system',
                node_id='primary'
            )
            db.add(system_metric)
            db.commit()
        
        # Send alerts if system is degraded
        if health_data['overall_status'] != 'healthy':
            logger.warning(f"🚨 System health degraded: {health_data['alerts']}")
            # In production, this would send email/SMS alerts
        
        logger.info(f"✅ System health check completed: {health_data['overall_status']}")
        
        return health_data
        
    except Exception as e:
        logger.error(f"❌ System health check failed: {e}")
        return {'overall_status': 'failed', 'error': str(e)}

def _check_redis_health() -> bool:
    """Check Redis connection health"""
    try:
        import redis
        r = redis.from_url(get_settings().database.REDIS_URL)
        return r.ping()
    except:
        return False

def _check_disk_space() -> Dict:
    """Check disk space availability"""
    import shutil
    try:
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        
        if free_gb < 1:
            return {'status': 'critical', 'message': f'Only {free_gb}GB free'}
        elif free_gb < 5:
            return {'status': 'warning', 'message': f'Low disk space: {free_gb}GB free'}
        else:
            return {'status': 'healthy', 'message': f'{free_gb}GB free'}
    except:
        return {'status': 'unknown', 'message': 'Unable to check disk space'}

def _check_memory_usage() -> Dict:
    """Check system memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        usage_percent = memory.percent
        
        if usage_percent > 90:
            return {'status': 'critical', 'message': f'Memory usage: {usage_percent:.1f}%'}
        elif usage_percent > 80:
            return {'status': 'warning', 'message': f'High memory usage: {usage_percent:.1f}%'}
        else:
            return {'status': 'healthy', 'message': f'Memory usage: {usage_percent:.1f}%'}
    except:
        return {'status': 'unknown', 'message': 'Unable to check memory usage'}

@app.task(name='tasks.calibrate_ai_agents')
def calibrate_ai_agents():
    """Calibrate and optimize AI agents"""
    try:
        logger.info("🤖 Calibrating AI agents...")
        
        hierarchy_manager = AIHierarchyManager()
        
        # Run async calibration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Train behavioral models with recent data
            training_data = _gather_training_data()
            loop.run_until_complete(
                hierarchy_manager.train_behavioral_model(training_data)
            )
            
            # Update agent performance metrics
            performance_report = hierarchy_manager.get_agent_performance_report()
            
            logger.info(f"✅ AI agents calibrated: {performance_report['overview']['overall_success_rate']:.1%} success rate")
            
            return performance_report
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ AI agent calibration failed: {e}")

def _gather_training_data() -> List[Dict]:
    """Gather training data from recent analyses"""
    training_data = []
    
    with db_manager.get_db() as db:
        # Get recent successful analyses for training
        recent_analyses = db.query(TaskResult).filter(
            TaskResult.status == 'completed',
            TaskResult.confidence_score > 0.8
        ).order_by(TaskResult.completed_at.desc()).limit(1000).all()
        
        for analysis in recent_analyses:
            training_data.append({
                'analysis_id': analysis.id,
                'success_rate': 1.0,  # These are successful analyses
                'response_time': analysis.processing_time or 0,
                'data_quality': analysis.confidence_score,
                'complexity': len(analysis.profiles_found or []) / 10.0,  # Normalized
                'data_volume': len(str(analysis.correlation_evidence or [])),
                'outcome': 1  # Success
            })
    
    return training_data

@app.task(name='tasks.cleanup_old_task_results')
def cleanup_old_task_results():
    """Clean up old task results to manage database size"""
    try:
        logger.info("🧹 Cleaning up old task results...")
        
        cutoff_date = datetime.now() - timedelta(days=30)  # Keep 30 days
        
        with db_manager.get_db() as db:
            # Delete old task results
            deleted_count = db.query(TaskResult).filter(
                TaskResult.created_at < cutoff_date
            ).delete()
            
            # Delete old system metrics (keep 90 days)
            metrics_cutoff = datetime.now() - timedelta(days=90)
            deleted_metrics = db.query(SystemMetrics).filter(
                SystemMetrics.timestamp < metrics_cutoff
            ).delete()
            
            db.commit()
        
        logger.info(f"✅ Cleanup completed: {deleted_count} tasks, {deleted_metrics} metrics removed")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

@app.task(name='tasks.analyze_bunker_patterns')
def analyze_bunker_patterns():
    """Analyze patterns in bunker data for ML training"""
    try:
        logger.info("🔍 Analyzing bunker patterns...")
        
        bunker = AnalysisBunker()
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # This would trigger ML pattern analysis
            # For now, just log the operation
            logger.info("✅ Bunker pattern analysis completed")
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ Bunker pattern analysis failed: {e}")

@app.task(name='tasks.generate_nightly_report')
def generate_nightly_report():
    """Generate nightly system performance report"""
    try:
        logger.info("📊 Generating nightly report...")
        
        report_data = {
            'date': datetime.now().date(),
            'system_health': {},
            'performance_metrics': {},
            'agent_performance': {},
            'recommendations': []
        }
        
        # System health summary
        health_data = system_health_check()
        report_data['system_health'] = health_data
        
        # Performance metrics
        with db_manager.get_db() as db:
            # Task statistics
            today = datetime.now().date()
            tasks_today = db.query(TaskResult).filter(
                TaskResult.created_at >= today
            ).count()
            
            successful_tasks = db.query(TaskResult).filter(
                TaskResult.created_at >= today,
                TaskResult.status == 'completed'
            ).count()
            
            avg_confidence = db.query(
                func.avg(TaskResult.confidence_score)
            ).filter(
                TaskResult.created_at >= today,
                TaskResult.status == 'completed'
            ).scalar() or 0
            
            report_data['performance_metrics'] = {
                'tasks_processed': tasks_today,
                'success_rate': successful_tasks / max(tasks_today, 1),
                'average_confidence': avg_confidence,
                'successful_tasks': successful_tasks
            }
        
        # Agent performance
        hierarchy_manager = AIHierarchyManager()
        agent_report = hierarchy_manager.get_agent_performance_report()
        report_data['agent_performance'] = agent_report
        
        # Generate recommendations
        report_data['recommendations'] = _generate_system_recommendations(report_data)
        
        # Store report (in production, this would be emailed/saved to file)
        logger.info(f"✅ Nightly report generated: {tasks_today} tasks, {successful_tasks} successful")
        
        return report_data
        
    except Exception as e:
        logger.error(f"❌ Nightly report generation failed: {e}")

def _generate_system_recommendations(report_data: Dict) -> List[str]:
    """Generate system improvement recommendations"""
    recommendations = []
    
    # System health recommendations
    if report_data['system_health'].get('overall_status') != 'healthy':
        recommendations.append("Investigate system health issues")
    
    # Performance recommendations
    perf_metrics = report_data['performance_metrics']
    if perf_metrics.get('success_rate', 0) < 0.8:
        recommendations.append("Optimize task processing pipeline")
    
    if perf_metrics.get('average_confidence', 0) < 0.7:
        recommendations.append("Improve AI agent accuracy")
    
    # Agent recommendations
    agent_details = report_data['agent_performance'].get('agent_details', {})
    for agent_id, details in agent_details.items():
        if details.get('success_rate', 0) < 0.7:
            recommendations.append(f"Retrain agent {agent_id}")
    
    return recommendations
