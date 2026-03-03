from flask import Blueprint, render_template

# 定义首页蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    渲染平台首页
    module_name='home' 会传递给 base.html，从而激活 style.css 里的首页专用全屏样式。
    """
    return render_template("index.html", module_name='home')