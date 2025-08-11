"""
VideoPlanet   
N+1  ,  ,  
"""

from django.db import models
from django.db.models import Prefetch, Count, Q, F, Sum
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class OptimizedQueryMixin:
    """    """
    
    def get_optimized_queryset(self):
        """  """
        queryset = super().get_queryset()
        
        #    
        model_name = self.model.__name__.lower()
        
        optimization_strategies = {
            'project': self._optimize_project_queryset,
            'feedback': self._optimize_feedback_queryset,
            'user': self._optimize_user_queryset,
            'videoplanning': self._optimize_videoplanning_queryset
        }
        
        if model_name in optimization_strategies:
            queryset = optimization_strategies[model_name](queryset)
            
        return queryset
        
    def _optimize_project_queryset(self, queryset):
        """  """
        return queryset.select_related(
            'user',
            'basic_plan'
        ).prefetch_related(
            'members',
            'schedule_set',
            Prefetch(
                'files',
                queryset=self.model.files.model.objects.filter(
                    is_deleted=False
                ).only('id', 'file_name', 'file_url', 'created_at')
            )
        ).annotate(
            member_count=Count('members'),
            file_count=Count('files', filter=Q(files__is_deleted=False)),
            schedule_count=Count('schedule_set')
        )
        
    def _optimize_feedback_queryset(self, queryset):
        """  """
        return queryset.select_related(
            'user',
            'project'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=self.model.comments.model.objects.select_related(
                    'user'
                ).only(
                    'id', 'content', 'time_stamp', 'created_at',
                    'user__id', 'user__name', 'user__profile_image'
                ).order_by('time_stamp')
            ),
            Prefetch(
                'reactions',
                queryset=self.model.reactions.model.objects.select_related(
                    'user'
                ).only('id', 'reaction', 'user__id', 'user__name')
            )
        ).annotate(
            comment_count=Count('comments'),
            reaction_count=Count('reactions')
        )
        
    def _optimize_user_queryset(self, queryset):
        """  """
        return queryset.prefetch_related(
            'projects_as_owner',
            'projects_as_member',
            'notifications'
        ).annotate(
            owned_project_count=Count('projects_as_owner'),
            member_project_count=Count('projects_as_member'),
            unread_notification_count=Count(
                'notifications',
                filter=Q(notifications__is_read=False)
            )
        )
        
    def _optimize_videoplanning_queryset(self, queryset):
        """   """
        return queryset.select_related(
            'user',
            'project'
        ).prefetch_related(
            'images',
            'storyboards'
        ).only(
            'id', 'title', 'genre', 'concept', 'created_at',
            'user__id', 'user__name',
            'project__id', 'project__title'
        )


class CacheOptimizationMixin:
    """    """
    
    cache_timeout = 300  # 5
    
    def get_cached_or_compute(self, cache_key, compute_func, timeout=None):
        """     """
        if timeout is None:
            timeout = self.cache_timeout
            
        result = cache.get(cache_key)
        if result is None:
            result = compute_func()
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache miss for {cache_key}, computed and cached")
        else:
            logger.debug(f"Cache hit for {cache_key}")
            
        return result
        
    def invalidate_cache_pattern(self, pattern):
        """    """
        from django.core.cache import cache
        from django.core.cache.backends.base import DEFAULT_TIMEOUT
        
        if hasattr(cache, '_cache'):
            # Redis  
            try:
                keys = cache._cache.keys(f"*{pattern}*")
                if keys:
                    cache.delete_many([key.decode() for key in keys])
                    logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
            except Exception as e:
                logger.error(f"Failed to invalidate cache pattern {pattern}: {e}")


class DatabaseIndexManager:
    """   """
    
    @staticmethod
    def create_missing_indexes():
        """  """
        from django.db import connection
        
        index_definitions = [
            #   
            {
                'name': 'idx_project_user_status',
                'table': 'projects_project',
                'columns': ['user_id', 'status'],
                'condition': None
            },
            {
                'name': 'idx_project_created_at',
                'table': 'projects_project',
                'columns': ['created_at'],
                'condition': None
            },
            #   
            {
                'name': 'idx_feedback_user_created',
                'table': 'feedbacks_feedback',
                'columns': ['user_id', 'created_at'],
                'condition': None
            },
            {
                'name': 'idx_feedback_project',
                'table': 'feedbacks_feedback',
                'columns': ['project_id'],
                'condition': 'project_id IS NOT NULL'
            },
            #   
            {
                'name': 'idx_feedback_comment_feedback',
                'table': 'feedbacks_feedbackcomment',
                'columns': ['feedback_id', 'time_stamp'],
                'condition': None
            },
            #   
            {
                'name': 'idx_user_email',
                'table': 'users_user',
                'columns': ['email'],
                'condition': None
            },
            {
                'name': 'idx_user_login_method',
                'table': 'users_user',
                'columns': ['login_method'],
                'condition': None
            },
            #   
            {
                'name': 'idx_videoplanning_user',
                'table': 'video_planning_videoplanning',
                'columns': ['user_id', 'created_at'],
                'condition': None
            }
        ]
        
        created_indexes = []
        
        with connection.cursor() as cursor:
            for index_def in index_definitions:
                try:
                    #    
                    cursor.execute(
                        "SELECT 1 FROM pg_indexes WHERE indexname = %s",
                        [index_def['name']]
                    )
                    
                    if not cursor.fetchone():
                        #  
                        columns_str = ', '.join(index_def['columns'])
                        condition_str = f" WHERE {index_def['condition']}" if index_def['condition'] else ""
                        
                        sql = f"""
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_def['name']}
                        ON {index_def['table']} ({columns_str}){condition_str}
                        """
                        
                        cursor.execute(sql)
                        created_indexes.append(index_def['name'])
                        logger.info(f"Created index: {index_def['name']}")
                        
                except Exception as e:
                    logger.error(f"Failed to create index {index_def['name']}: {e}")
                    
        return created_indexes
        
    @staticmethod
    def analyze_slow_queries():
        """  """
        from django.db import connection
        
        slow_queries = []
        
        with connection.cursor() as cursor:
            try:
                # pg_stat_statements    
                cursor.execute(
                    "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
                )
                
                if cursor.fetchone():
                    #    (   100ms )
                    cursor.execute("""
                        SELECT 
                            query,
                            calls,
                            mean_exec_time,
                            total_exec_time,
                            rows
                        FROM pg_stat_statements
                        WHERE mean_exec_time > 100
                        ORDER BY mean_exec_time DESC
                        LIMIT 20
                    """)
                    
                    for row in cursor.fetchall():
                        slow_queries.append({
                            'query': row[0][:200],  #   200
                            'calls': row[1],
                            'mean_time_ms': row[2],
                            'total_time_ms': row[3],
                            'rows': row[4]
                        })
                        
            except Exception as e:
                logger.error(f"Failed to analyze slow queries: {e}")
                
        return slow_queries
        
    @staticmethod
    def optimize_database_settings():
        """   """
        from django.db import connection
        
        recommendations = []
        
        with connection.cursor() as cursor:
            try:
                #   
                settings_to_check = [
                    ('shared_buffers', '256MB', ' 25% '),
                    ('effective_cache_size', '1GB', ' 50-75% '),
                    ('work_mem', '4MB', '   '),
                    ('maintenance_work_mem', '64MB', 'VACUUM  '),
                    ('random_page_cost', '4', 'SSD  1.1 '),
                    ('checkpoint_completion_target', '0.9', '  '),
                    ('wal_buffers', '16MB', 'Write  '),
                    ('default_statistics_target', '100', '   ')
                ]
                
                for setting_name, recommended, description in settings_to_check:
                    cursor.execute(
                        "SELECT setting FROM pg_settings WHERE name = %s",
                        [setting_name]
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        current_value = result[0]
                        recommendations.append({
                            'setting': setting_name,
                            'current': current_value,
                            'recommended': recommended,
                            'description': description
                        })
                        
            except Exception as e:
                logger.error(f"Failed to get database settings: {e}")
                
        return recommendations


class QueryPerformanceMonitor:
    """   """
    
    @staticmethod
    def log_slow_query(query, execution_time, view_name=None):
        """  """
        if execution_time > 1.0:  # 1 
            logger.warning(
                f"Slow query detected in {view_name or 'unknown'}: "
                f"{execution_time:.2f}s - {query[:200]}"
            )
            
            #   
            cache_key = f"slow_query_stats_{timezone.now().strftime('%Y%m%d')}"
            stats = cache.get(cache_key, [])
            stats.append({
                'query': query[:500],
                'execution_time': execution_time,
                'view_name': view_name,
                'timestamp': timezone.now().isoformat()
            })
            cache.set(cache_key, stats, 86400)  # 24 
            
    @staticmethod
    def get_query_statistics():
        """  """
        from django.db import connection
        
        stats = {
            'total_queries': 0,
            'slow_queries': [],
            'most_frequent': [],
            'recommendations': []
        }
        
        #    
        cache_key = f"slow_query_stats_{timezone.now().strftime('%Y%m%d')}"
        slow_queries = cache.get(cache_key, [])
        
        if slow_queries:
            stats['slow_queries'] = sorted(
                slow_queries,
                key=lambda x: x['execution_time'],
                reverse=True
            )[:10]
            
        # N+1  
        with connection.cursor() as cursor:
            stats['total_queries'] = len(connection.queries)
            
            #      N+1  
            query_patterns = {}
            for query in connection.queries:
                # SELECT  
                if query['sql'].startswith('SELECT'):
                    #   (  )
                    pattern = query['sql'].split('FROM')[1].split('WHERE')[0].strip() if 'FROM' in query['sql'] else ''
                    if pattern:
                        query_patterns[pattern] = query_patterns.get(pattern, 0) + 1
                        
            # 5    N+1  
            for pattern, count in query_patterns.items():
                if count > 5:
                    stats['recommendations'].append({
                        'type': 'n_plus_one',
                        'pattern': pattern,
                        'count': count,
                        'suggestion': 'select_related()  prefetch_related()  '
                    })
                    
        return stats


class BulkOperationOptimizer:
    """   """
    
    @staticmethod
    def bulk_create_with_batch(model_class, objects, batch_size=1000):
        """   """
        created_objects = []
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            created = model_class.objects.bulk_create(batch, ignore_conflicts=True)
            created_objects.extend(created)
            logger.info(f"Created batch {i//batch_size + 1}: {len(created)} objects")
            
        return created_objects
        
    @staticmethod
    def bulk_update_with_batch(model_class, objects, fields, batch_size=1000):
        """   """
        updated_count = 0
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            model_class.objects.bulk_update(batch, fields, batch_size=batch_size)
            updated_count += len(batch)
            logger.info(f"Updated batch {i//batch_size + 1}: {len(batch)} objects")
            
        return updated_count
        
    @staticmethod
    def efficient_delete(queryset, batch_size=1000):
        """   (  )"""
        if hasattr(queryset.model, 'is_deleted'):
            #  
            return queryset.update(is_deleted=True, deleted_at=timezone.now())
        else:
            #   ( )
            deleted_count = 0
            while True:
                batch = list(queryset[:batch_size].values_list('pk', flat=True))
                if not batch:
                    break
                    
                count, _ = queryset.filter(pk__in=batch).delete()
                deleted_count += count
                logger.info(f"Deleted batch: {count} objects")
                
            return deleted_count