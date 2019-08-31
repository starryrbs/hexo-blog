from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run

REPO_URL = 'https://github.com/starryrbs/hexo-blog.git'

PROJECT_NAME = 'hexo-blog'


def remote_exist(file_path):
    """

    判断远端文件是否存在

    :return: 布尔值

    """

    if int(run(" [ -e " + file_path + " ] && echo 11 || echo 10")) == 11:
        return True
    else:
        return False


def _create_directory_structure_if_necessary(source_folder):
    if not remote_exist(source_folder):
        run(f'mkdir -p {source_folder}')


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


def _run_hexo_command(site_folder):
    run(f'cd {site_folder}')
    run(f'hexo clean&&hexo g&&hexo d')


def remove_readme(source_folder):
    readme_file_path = f'{source_folder}/README.md'
    if remote_exist(readme_file_path):
        run(f'rm -rf {readme_file_path}')


def deploy():
    site_folder = f'/projects/hexo'
    source_folder = site_folder + f'/source/_posts/{PROJECT_NAME}/'
    _create_directory_structure_if_necessary(source_folder)
    _get_latest_source(source_folder)
    remove_readme(source_folder)
    _run_hexo_command(site_folder)
