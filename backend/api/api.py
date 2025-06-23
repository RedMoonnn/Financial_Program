from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.services.services import TaskService, FlowDataService, FlowImageService, CacheService, init_db
from backend.crawler.crawler import fetch_flow_data
from backend.api.health import health_bp
import logging
import traceback
from backend.ai.deepseek import DeepseekAgent

app = Flask(__name__)
CORS(app)

# 注册健康检查蓝图
app.register_blueprint(health_bp)

# 初始化数据库
init_db()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {e}\n{traceback.format_exc()}")
    return jsonify({'error': '服务器内部错误', 'detail': str(e)}), 500

@app.route('/api/collect', methods=['POST'])
def collect():
    """
    触发采集任务，参数：flow_type, market_type, period, pages
    返回：任务ID
    """
    try:
        data = request.json
        flow_type = data['flow_type']
        market_type = data['market_type']
        period = data['period']
        pages = int(data.get('pages', 1))
        # 创建采集任务
        task = TaskService.create_task(flow_type, market_type, period, pages)
        # 采集数据
        try:
            flow_data = fetch_flow_data(flow_type, market_type, period, pages)
            FlowDataService.save_flow_data(flow_data, task.id)
            # 缓存每条数据
            for item in flow_data:
                CacheService.cache_flow_data(item['code'], flow_type, market_type, period, item)
            TaskService.update_task_status(task.id, 'success')
        except Exception as e:
            TaskService.update_task_status(task.id, 'failed', error_msg=str(e))
            logger.error(f"采集失败: {e}")
            return jsonify({'error': '采集失败', 'detail': str(e)}), 500
        logger.info(f"采集任务成功: {task.id}")
        return jsonify({'task_id': task.id}), 200
    except Exception as e:
        logger.error(f"参数错误: {e}")
        return jsonify({'error': '参数错误', 'detail': str(e)}), 400

@app.route('/api/flow', methods=['GET'])
def get_flow():
    """
    查询资金流数据，参数：code, flow_type, market_type, period
    优先查Redis缓存
    """
    code = request.args.get('code')
    flow_type = request.args.get('flow_type')
    market_type = request.args.get('market_type')
    period = request.args.get('period')
    # 查缓存
    data = CacheService.get_cached_flow_data(code, flow_type, market_type, period)
    if data:
        return jsonify({'data': data, 'cached': True})
    # TODO: 可加数据库兜底查询
    return jsonify({'error': '未找到数据'}), 404

@app.route('/api/image', methods=['GET'])
def get_image():
    """
    查询图片URL，参数：code, flow_type, market_type, period
    优先查Redis缓存
    """
    code = request.args.get('code')
    flow_type = request.args.get('flow_type')
    market_type = request.args.get('market_type')
    period = request.args.get('period')
    url = CacheService.get_cached_image_url(code, flow_type, market_type, period)
    if url:
        return jsonify({'image_url': url, 'cached': True})
    # TODO: 可加数据库兜底查询
    return jsonify({'error': '未找到图片'}), 404

@app.route('/api/task/<int:task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    查询采集任务状态
    """
    from backend.models.models import SessionLocal, FlowTask
    session = SessionLocal()
    task = session.query(FlowTask).filter_by(id=task_id).first()
    if not task:
        session.close()
        return jsonify({'error': '任务不存在'}), 404
    result = {
        'id': task.id,
        'flow_type': task.flow_type,
        'market_type': task.market_type,
        'period': task.period,
        'pages': task.pages,
        'status': task.status.value,
        'start_time': str(task.start_time),
        'end_time': str(task.end_time) if task.end_time else None,
        'error_msg': task.error_msg
    }
    session.close()
    return jsonify(result)

@app.route('/api/ai/agent', methods=['POST'])
def ai_agent():
    try:
        data = request.json
        flow_type = data.get('flow_type')
        market_type = data.get('market_type')
        period = data.get('period')
        code = data.get('code')
        style = data.get('style', '专业')
        user_message = data.get('message')
        history = data.get('history', [])
        # 查询个股资金流
        flow_data = FlowDataService.get_latest_flow_data(code, flow_type, market_type, period)
        # 查询板块资金流（如有）
        sector_data = None
        if 'sector_flow_data' in data:
            sector_data = data['sector_flow_data']
        # 调用Agent分析
        result = DeepseekAgent.analyze(flow_data, sector_data, style, user_message, history)
        return result, 200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 