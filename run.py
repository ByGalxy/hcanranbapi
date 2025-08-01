from image_api import create_app
"""
比起写代码，我更喜欢你~~~~

看这里~

配置环境:venv\Scripts\activate
运行代码:python run.py
"""


app = create_app()

if __name__ == '__main__':
    app.run(port=5000)