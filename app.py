from flask import Flask
from config import Config
from core import formulas
from routes.main import main_bp
from routes.analysis import analysis_bp   # ⭐ 唯一实验入口
from services.record_service import init_record_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_record_db()

    # 注册首页蓝图（包含首页路由）
    app.register_blueprint(main_bp)
    
    # 注册实验分析蓝图（包含所有计算接口）
    app.register_blueprint(analysis_bp)

    return app


if __name__ == "__main__":
    # 启动开发服务器
    app = create_app()
    app.run(debug=True)
