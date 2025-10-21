# core/query_optimizer.py
from sqlalchemy import text
from typing import List, Dict, Any
import logging

class QueryOptimizer:
    def __init__(self, db_session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    async def optimize_search_query(self, filters: Dict[str, Any]) -> str:
        """Optimize search queries based on filters"""
        base_query = """
            SELECT * FROM task_results 
            WHERE 1=1
        """
        
        conditions = []
        params = {}
        
        # Add conditions based on available filters
        if filters.get('email'):
            conditions.append("email = :email")
            params['email'] = filters['email']
            
        if filters.get('platform'):
            conditions.append("platform = :platform")
            params['platform'] = filters['platform']
            
        if filters.get('date_from'):
            conditions.append("created_at >= :date_from")
            params['date_from'] = filters['date_from']
            
        if filters.get('date_to'):
            conditions.append("created_at <= :date_to")
            params['date_to'] = filters['date_to']
            
        # Build final query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
            
        # Add ordering and limiting
        base_query += " ORDER BY confidence_score DESC, created_at DESC"
        
        if filters.get('limit'):
            base_query += " LIMIT :limit"
            params['limit'] = filters['limit']
            
        return text(base_query), params

    async def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN"""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
        
        try:
            result = await self.db.execute(text(explain_query))
            plan = result.fetchone()[0]
            
            return {
                'execution_time': plan[0]['Planning Time'] + plan[0]['Execution Time'],
                'rows_affected': plan[0]['Plan']['Actual Rows'],
                'buffer_hits': plan[0]['Plan']['Shared Hit Blocks'],
                'buffer_reads': plan[0]['Plan']['Shared Read Blocks']
            }
        except Exception as e:
            self.logger.error(f"Query analysis failed: {str(e)}")
            return {}
