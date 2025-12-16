# dflow OP 模块
# 使用延迟导入避免依赖冲突

__all__ = [
    # 原有 OP
    "CrawlStockFlowOP",
    "CrawlSectorFlowOP",
    "StoreToMySQLOP",
    "StoreSingleFileOP",
    "AIAnalysisOP",
    "GenerateReportOP",
    # 新增批量 OP
    "BatchCrawlStockFlowOP",
    "BatchCrawlSectorFlowOP",
    "BatchStoreToMySQLOP",
    "DeepSeekAnalysisOP",
    "StoreReportToMinIOOP",
]


def __getattr__(name):  # noqa: F401
    """延迟导入 OP 类"""
    if name == "CrawlStockFlowOP":
        from .crawl_op import CrawlStockFlowOP

        return CrawlStockFlowOP
    elif name == "CrawlSectorFlowOP":
        from .crawl_op import CrawlSectorFlowOP

        return CrawlSectorFlowOP
    elif name == "StoreToMySQLOP":
        from .store_op import StoreToMySQLOP

        return StoreToMySQLOP
    elif name == "StoreSingleFileOP":
        from .store_op import StoreSingleFileOP

        return StoreSingleFileOP
    elif name == "AIAnalysisOP":
        from .ai_op import AIAnalysisOP

        return AIAnalysisOP
    elif name == "GenerateReportOP":
        from .report_op import GenerateReportOP

        return GenerateReportOP
    elif name == "BatchCrawlStockFlowOP":
        from .batch_crawl_op import BatchCrawlStockFlowOP

        return BatchCrawlStockFlowOP
    elif name == "BatchCrawlSectorFlowOP":
        from .batch_crawl_op import BatchCrawlSectorFlowOP

        return BatchCrawlSectorFlowOP
    elif name == "BatchStoreToMySQLOP":
        from .batch_store_op import BatchStoreToMySQLOP

        return BatchStoreToMySQLOP
    elif name == "DeepSeekAnalysisOP":
        from .deepseek_analysis_op import DeepSeekAnalysisOP

        return DeepSeekAnalysisOP
    elif name == "StoreReportToMinIOOP":
        from .minio_store_op import StoreReportToMinIOOP

        return StoreReportToMinIOOP
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
