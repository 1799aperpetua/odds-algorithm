from setuptools import setup

setup(
    app = ['main.py', 'script.py'],
    options = {
        'py2app' : {
            'packages' : ['customtkinter', 'requests', 'json', 'sqlite3']
        }
    }
)