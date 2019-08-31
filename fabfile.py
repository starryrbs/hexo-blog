import random

from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run

REPO_URL = 'https://github.com/starryrbs/django_test.git'

PROJECT_NAME = 'django_test'


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run(f'mkdir -p {site_folder}/{subfolder}')


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        # 在现有仓库中执行 git fetch 命令的作用是从网络中拉取最新提交（与 git pull 类
        # 似，但是不会立即更新线上源码）
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    # 我们捕获 git log 命令的输出，获取本地仓库中当
    # 前提交的 ID。这么做的结果是，服务器中代码将和本地检出的代码版本一致（前提是
    # 已经把代码推送到服务器）。
    current_commit = local('git log -n 1 --format=%H', capture=True)
    # 执行 git reset --hard 命令，切换到指定的提交。这个命令会撤销在服务器中对代码
    # 仓库所做的任何改动。
    run(f'cd {source_folder} && git reset --hard {current_commit}')


def _update_settings(source_folder, site_name):
    settings_path = source_folder + f'/{PROJECT_NAME}/settings.py'
    # sed 函数的作用是在文件中替换字符串
    sed(settings_path, 'DEBUG = True', "DEBUG = False")
    # sed 调整 ALLOWED_HOSTS 的值，使用正则表达式匹配正确的代码行。
    sed(settings_path, 'ALLOWED_HOSTS = .+$', f'ALLOWED_HOSTS = ["{site_name}"]')
    secret_key_file = source_folder + f'/{PROJECT_NAME}/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        # append 的作用是在文件末尾添加一行内容。（
        append(secret_key_file, f'SECRET_KEY = "{key}"')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run(f'python3 -m venv {virtualenv_folder}')
    run(
        f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple')


def _update_static_files(source_folder):
    run(f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
        )


def _run_server(source_folder):
    run(f'cd {source_folder}'
        ' && nohup ../virtualenv/bin/python manage.py runserver 0.0.0.0:12345 &'
        )


# 1. 

def test():
    run(f'dir')


def deploy():
    site_folder = f'/home/sites'
    source_folder = site_folder + '/source'
    test()
