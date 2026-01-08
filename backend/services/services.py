"""
服务层统一导出模块（保持向后兼容）
所有服务类都从各自的模块导入，这里只负责统一导出
"""
# 从新模块导入所有服务类（保持向后兼容）

# 全局数据采集状态（保持向后兼容，已废弃，请使用 get_data_ready()）
DATA_READY = False

# 注意：Redis客户端应该通过 CacheService 或 EmailService 访问
# 这里不再提供全局 redis_client，避免重复初始化
