# dflow 工作流模块
# 使用延迟导入避免依赖问题

__all__ = [
    "create_full_pipeline",
    "create_incremental_pipeline",
    "create_hello_workflow",
    "create_crawl_workflow",
]


def __getattr__(name):
    """延迟导入工作流函数"""
    if name == "create_full_pipeline":
        from .full_pipeline import create_full_pipeline

        return create_full_pipeline
    elif name == "create_incremental_pipeline":
        from .incremental import create_incremental_pipeline

        return create_incremental_pipeline
    elif name == "create_hello_workflow":
        from .simple_test import create_hello_workflow

        return create_hello_workflow
    elif name == "create_crawl_workflow":
        from .simple_test import create_crawl_workflow

        return create_crawl_workflow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
