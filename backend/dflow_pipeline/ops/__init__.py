# dflow OP 模块
# 使用延迟导入避免依赖冲突

__all__ = [
    "CrawlStockFlowOP",
    "CrawlSectorFlowOP",
    "StoreToMySQLOP",
    "StoreSingleFileOP",
    "AIAnalysisOP",
    "GenerateReportOP",
]


def __getattr__(name):
    """延迟导入 OP 类"""
    if name in ("CrawlStockFlowOP", "CrawlSectorFlowOP"):
        from .crawl_op import CrawlStockFlowOP, CrawlSectorFlowOP
        return locals()[name]
    elif name in ("StoreToMySQLOP", "StoreSingleFileOP"):
        from .store_op import StoreToMySQLOP, StoreSingleFileOP
        return locals()[name]
    elif name == "AIAnalysisOP":
        from .ai_op import AIAnalysisOP
        return AIAnalysisOP
    elif name == "GenerateReportOP":
        from .report_op import GenerateReportOP
        return GenerateReportOP
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
