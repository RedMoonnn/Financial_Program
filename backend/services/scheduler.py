"""
定时任务调度模块
统一管理所有定时任务
"""

import json
import logging
import tempfile

from apscheduler.schedulers.background import BackgroundScheduler
from core.database import get_db_session
from core.storage import minio_storage
from models.models import User

from services.ai.deepseek import DeepseekAgent
from services.report.report_service import ReportService

logger = logging.getLogger(__name__)


def generate_daily_reports():
    """
    生成每日报告（定时任务）
    注意：此功能需要进一步优化，当前实现仅供参考
    """
    try:
        with get_db_session() as session:
            users = session.query(User).all()
            for user in users:
                # 获取业务数据（如今日flow数据）
                flow_data = []  # TODO: 获取用户相关数据
                # 标准化prompt
                prompt = f"""
你是一个专业的金融智能分析助手。请根据以下业务数据，为用户生成一份结构化、详实、专业的每日金融分析报告，内容包括但不限于：市场综述、个股表现、主力资金流向、风险提示、投资建议等。请以Markdown格式输出完整报告，内容条理清晰、数据准确、图表丰富，适合直接给用户在线预览或下载。

【业务数据】
{json.dumps(flow_data, ensure_ascii=False)}

【要求】
- 报告格式：Markdown
- 报告内容：包含市场综述、个股表现、主力资金流向、风险提示、投资建议等
- 图表：如有必要可用Markdown语法插入图片或表格
- 语言：中文
- 结构：有目录、分章节、图文并茂
- 输出：返回完整Markdown文本

请直接生成并返回Markdown格式的完整报告内容。
"""
                result = DeepseekAgent.analyze(flow_data, style="专业", user_message=prompt)
                advice_text = result.get("advice", "")
                # 生成Markdown
                md_content = f"# {user.email} 每日分析报告\n\n{advice_text}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as f:
                    f.write(md_content.encode("utf-8"))
                    md_path = f.name
                md_url = minio_storage.upload_image(md_path)
                # 写入MySQL
                ReportService.add_report(user.id, "markdown", md_url, md_path.split("/")[-1])
                logger.info(f"已为用户 {user.email} 生成每日报告")
    except Exception as e:
        logger.error(f"生成每日报告失败: {e}", exc_info=True)


def init_scheduler():
    """初始化定时任务调度器"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        generate_daily_reports, "cron", hour=0, minute=0, id="daily_reports", replace_existing=True
    )
    scheduler.start()
    logger.info("定时任务调度器已启动")
    return scheduler
