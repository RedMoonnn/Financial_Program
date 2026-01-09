import datetime
import enum
from datetime import timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def beijing_now():
    return datetime.datetime.now(timezone(datetime.timedelta(hours=8)))


class TaskStatus(enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class FlowTask(Base):
    __tablename__ = "flow_task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    flow_type = Column(String(32), nullable=False)
    market_type = Column(String(64), nullable=False)
    period = Column(String(16), nullable=False)
    pages = Column(Integer, default=1)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    start_time = Column(DateTime, default=beijing_now)
    end_time = Column(DateTime)
    error_msg = Column(Text)
    # 反向引用
    flow_data = relationship("FlowData", back_populates="task")
    flow_images = relationship("FlowImage", back_populates="task")


class FlowData(Base):
    __tablename__ = "flow_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    flow_type = Column(String(32), nullable=False)
    market_type = Column(String(64), nullable=False)
    period = Column(String(16), nullable=False)
    latest_price = Column(Float)
    change_percentage = Column(Float)
    main_flow_net_amount = Column(Float)
    main_flow_net_percentage = Column(Float)
    extra_large_order_flow_net_amount = Column(Float)
    extra_large_order_flow_net_percentage = Column(Float)
    large_order_flow_net_amount = Column(Float)
    large_order_flow_net_percentage = Column(Float)
    medium_order_flow_net_amount = Column(Float)
    medium_order_flow_net_percentage = Column(Float)
    small_order_flow_net_amount = Column(Float)
    small_order_flow_net_percentage = Column(Float)
    crawl_time = Column(DateTime, default=beijing_now)
    task_id = Column(Integer, ForeignKey("flow_task.id"))
    task = relationship("FlowTask", back_populates="flow_data")
    __table_args__ = (
        Index(
            "idx_code_type_period_task",
            "code",
            "flow_type",
            "market_type",
            "period",
            "task_id",
            unique=True,
        ),
    )


class FlowImage(Base):
    __tablename__ = "flow_image"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(16), nullable=False)
    flow_type = Column(String(32), nullable=False)
    market_type = Column(String(64), nullable=False)
    period = Column(String(16), nullable=False)
    image_url = Column(String(256), nullable=False)
    crawl_time = Column(DateTime, default=beijing_now)
    task_id = Column(Integer, ForeignKey("flow_task.id"))
    task = relationship("FlowTask", back_populates="flow_images")
    __table_args__ = (
        Index(
            "idx_img_code_type_period_task",
            "code",
            "flow_type",
            "market_type",
            "period",
            "task_id",
            unique=True,
        ),
    )


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=True, index=True)  # 登录账号（可选）
    email = Column(String(128), unique=True, nullable=False, index=True)  # 邮箱（用于验证码）
    password_hash = Column(String(256), nullable=False)
    is_active = Column(Integer, default=1)  # 1=激活，0=未激活
    is_admin = Column(Integer, default=0)  # 1=管理员，0=普通用户
    created_at = Column(DateTime, default=beijing_now)
    # 可扩展字段：昵称、头像、角色等
    # 反向引用：用户的报告、任务等


class Report(Base):
    __tablename__ = "report"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    report_type = Column(String(32), nullable=False)  # pdf/markdown
    file_url = Column(Text, nullable=False)  # MinIO URL (使用Text类型以支持预签名URL的长查询参数)
    file_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=beijing_now)
    # 可扩展字段：摘要、状态等
