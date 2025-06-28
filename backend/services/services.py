from models.models import Base, FlowTask, FlowData, FlowImage, TaskStatus, User, Report
from cache.cache import redis_cache
from storage.storage import minio_storage
from utils.utils import get_now
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os
from sqlalchemy.exc import IntegrityError, OperationalError
from passlib.hash import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import redis
import random
import string
from apscheduler.schedulers.background import BackgroundScheduler
from ai.deepseek import DeepseekAgent
import tempfile
import time

# 创建数据库引擎和会话工厂
engine = create_engine(
    f"mysql+pymysql://{os.getenv('MYSQL_USER','root')}:{os.getenv('MYSQL_PASSWORD','')}@{os.getenv('MYSQL_HOST','localhost')}:{os.getenv('MYSQL_PORT','3306')}/{os.getenv('MYSQL_DATABASE','test')}?charset=utf8mb4",
    echo=False
)
SessionLocal = sessionmaker(bind=engine)

# 全局数据采集状态
DATA_READY = False

# 初始化数据库（如首次运行需建表）
def init_db(max_retries=30, delay=2):
    for i in range(max_retries):
        try:
            Base.metadata.create_all(engine)
            print("数据库连接成功！")
            # 自动创建管理员账号
            admin_email = os.getenv('ADMIN_EMAIL')
            admin_password = os.getenv('ADMIN_PASSWORD')
            if admin_email and admin_password:
                session = SessionLocal()
                user = session.query(User).filter_by(email=admin_email).first()
                if not user:
                    password_hash = bcrypt.hash(admin_password)
                    user = User(email=admin_email, password_hash=password_hash)
                    session.add(user)
                    session.commit()
                    print(f"已自动创建管理员账号: {admin_email}")
                session.close()
            return
        except OperationalError as e:
            print(f"数据库连接失败，第{i+1}次重试，错误信息：{e}")
            time.sleep(delay)
    raise Exception("多次重试后仍无法连接数据库，请检查 MySQL 服务！")

# 1. 采集任务相关服务
class TaskService:
    @staticmethod
    def create_task(flow_type, market_type, period, pages):
        session = SessionLocal()
        task = FlowTask(
            flow_type=flow_type,
            market_type=market_type,
            period=period,
            pages=pages,
            status=TaskStatus.pending,
            start_time=get_now()
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        session.close()
        return task

    @staticmethod
    def update_task_status(task_id, status, error_msg=None):
        session = SessionLocal()
        task = session.query(FlowTask).filter_by(id=task_id).first()
        if task:
            task.status = status
            task.end_time = get_now()
            if error_msg:
                task.error_msg = error_msg
            session.commit()
        session.close()

# 2. 资金流数据入库服务
class FlowDataService:
    @staticmethod
    def save_flow_data(data_list, task_id):
        session = SessionLocal()
        for data in data_list:
            flow_data = FlowData(
                code=data['code'],
                name=data['name'],
                flow_type=data['flow_type'],
                market_type=data['market_type'],
                period=data['period'],
                latest_price=data.get('latest_price'),
                change_percentage=data.get('change_percentage'),
                main_flow_net_amount=data.get('main_flow_net_amount'),
                main_flow_net_percentage=data.get('main_flow_net_percentage'),
                extra_large_order_flow_net_amount=data.get('extra_large_order_flow_net_amount'),
                extra_large_order_flow_net_percentage=data.get('extra_large_order_flow_net_percentage'),
                large_order_flow_net_amount=data.get('large_order_flow_net_amount'),
                large_order_flow_net_percentage=data.get('large_order_flow_net_percentage'),
                medium_order_flow_net_amount=data.get('medium_order_flow_net_amount'),
                medium_order_flow_net_percentage=data.get('medium_order_flow_net_percentage'),
                small_order_flow_net_amount=data.get('small_order_flow_net_amount'),
                small_order_flow_net_percentage=data.get('small_order_flow_net_percentage'),
                crawl_time=get_now(),
                task_id=task_id
            )
            session.merge(flow_data)  # merge可避免唯一索引冲突
        session.commit()
        session.close()

    @staticmethod
    def get_latest_flow_data(code, flow_type, market_type, period):
        session = SessionLocal()
        q = session.query(FlowData).filter_by(
            code=code,
            flow_type=flow_type,
            market_type=market_type,
            period=period
        ).order_by(FlowData.crawl_time.desc())
        result = q.first()
        session.close()
        if result:
            return {
                'code': result.code,
                'name': result.name,
                'flow_type': result.flow_type,
                'market_type': result.market_type,
                'period': result.period,
                'latest_price': result.latest_price,
                'change_percentage': result.change_percentage,
                'main_flow_net_amount': result.main_flow_net_amount,
                'main_flow_net_percentage': result.main_flow_net_percentage,
                'extra_large_order_flow_net_amount': result.extra_large_order_flow_net_amount,
                'extra_large_order_flow_net_percentage': result.extra_large_order_flow_net_percentage,
                'large_order_flow_net_amount': result.large_order_flow_net_amount,
                'large_order_flow_net_percentage': result.large_order_flow_net_percentage,
                'medium_order_flow_net_amount': result.medium_order_flow_net_amount,
                'medium_order_flow_net_percentage': result.medium_order_flow_net_percentage,
                'small_order_flow_net_amount': result.small_order_flow_net_amount,
                'small_order_flow_net_percentage': result.small_order_flow_net_percentage,
                'crawl_time': str(result.crawl_time)
            }
        return None

# 3. 图片上传与元数据入库服务
class FlowImageService:
    @staticmethod
    def save_image(file_path, code, flow_type, market_type, period, task_id):
        # 上传图片到MinIO
        object_name = minio_storage.upload_image(file_path)
        image_url = minio_storage.get_image_url(object_name)
        session = SessionLocal()
        flow_image = FlowImage(
            code=code,
            flow_type=flow_type,
            market_type=market_type,
            period=period,
            image_url=image_url,
            crawl_time=get_now(),
            task_id=task_id
        )
        session.merge(flow_image)
        session.commit()
        session.close()
        return image_url

# 4. Redis缓存服务
class CacheService:
    @staticmethod
    def cache_flow_data(code, flow_type, market_type, period, data, expire=3600):
        key = f"flow:{code}:{flow_type}:{market_type}:{period}"
        redis_cache.set(key, json.dumps(data), ex=expire)

    @staticmethod
    def get_cached_flow_data(code, flow_type, market_type, period):
        key = f"flow:{code}:{flow_type}:{market_type}:{period}"
        value = redis_cache.get(key)
        if value:
            return json.loads(value)
        return None

    @staticmethod
    def cache_image_url(code, flow_type, market_type, period, url, expire=3600):
        key = f"flowimg:{code}:{flow_type}:{market_type}:{period}"
        redis_cache.set(key, url, ex=expire)

    @staticmethod
    def get_cached_image_url(code, flow_type, market_type, period):
        key = f"flowimg:{code}:{flow_type}:{market_type}:{period}"
        return redis_cache.get(key)

# Redis连接（假设和cache一致）
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    password=os.getenv('REDIS_PASSWORD', ''),
    decode_responses=True
)

class UserService:
    @staticmethod
    def register(email, password):
        session = SessionLocal()
        if session.query(User).filter_by(email=email).first():
            session.close()
            raise Exception('邮箱已注册')
        password_hash = bcrypt.hash(password)
        user = User(email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        session.close()
        return True

    @staticmethod
    def verify_password(email, password):
        session = SessionLocal()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        if not user:
            return False
        return bcrypt.verify(password, user.password_hash)

    @staticmethod
    def get_user(email):
        session = SessionLocal()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        return user

    @staticmethod
    def set_password(email, new_password):
        session = SessionLocal()
        user = session.query(User).filter_by(email=email).first()
        if not user:
            session.close()
            raise Exception('用户不存在')
        user.password_hash = bcrypt.hash(new_password)
        session.commit()
        session.close()
        return True

class EmailService:
    @staticmethod
    def send_code(email, code):
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        # 优化邮件内容和发件人
        content = f'''尊敬的用户：\n\n您正在使用金融数据平台进行身份验证，本次验证码为：{code}。\n验证码5分钟内有效，请勿泄露给他人。\n\n如非本人操作，请忽略本邮件。\n\n—— 金融分析小助手\n'''
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = str(Header('金融分析小助手', 'utf-8')) + f' <{smtp_user}>'
        msg['To'] = email
        msg['Subject'] = Header('金融数据平台验证码', 'utf-8')
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [email], msg.as_string())
            server.quit()
        except Exception as e:
            raise Exception(f'邮件发送失败: {e}')

    @staticmethod
    def gen_and_store_code(email):
        code = ''.join(random.choices(string.digits, k=6))
        redis_client.setex(f'email:code:{email}', 300, code)
        return code

    @staticmethod
    def verify_code(email, code):
        real_code = redis_client.get(f'email:code:{email}')
        return real_code == code

class ReportService:
    @staticmethod
    def add_report(user_id, report_type, file_url, file_name):
        session = SessionLocal()
        report = Report(user_id=user_id, report_type=report_type, file_url=file_url, file_name=file_name)
        session.add(report)
        session.commit()
        session.close()
        return True

    @staticmethod
    def list_reports(user_id):
        session = SessionLocal()
        reports = session.query(Report).filter_by(user_id=user_id).order_by(Report.created_at.desc()).all()
        session.close()
        return reports

class ChatService:
    @staticmethod
    def save_history(user_id, history):
        redis_client.setex(f'chat:history:{user_id}', 7*24*3600, json.dumps(history))

    @staticmethod
    def get_history(user_id):
        data = redis_client.get(f'chat:history:{user_id}')
        if data:
            return json.loads(data)
        return []

    @staticmethod
    def clear_history(user_id):
        redis_client.delete(f'chat:history:{user_id}')

def generate_daily_reports():
    session = SessionLocal()
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
        advice = DeepseekAgent.analyze(flow_data, style="专业", user_message=prompt)
        # 生成Markdown
        md_content = f"# {user.email} 每日分析报告\n\n{advice}"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as f:
            f.write(md_content.encode('utf-8'))
            md_path = f.name
        md_url = minio_storage.upload_image(md_path)
        # 写入MySQL
        ReportService.add_report(user.id, 'markdown', md_url, md_path.split('/')[-1])
    session.close()

scheduler = BackgroundScheduler()
scheduler.add_job(generate_daily_reports, 'cron', hour=0, minute=0)
scheduler.start()

def set_data_ready(flag: bool):
    redis_cache.set('DATA_READY', '1' if flag else '0', ex=3600*24)

def get_data_ready():
    v = redis_cache.get('DATA_READY')
    return v == '1' 