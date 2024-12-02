import os
import subprocess

# 定义要执行的脚本列表
scripts_to_run = {
    'import_dataset.py': {},
    'morphingdb_test.py': {},
    'evadb_test.py': {}
}


dir_list = ['muti_query']


# 设置项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

def run_scripts_in_directory(directory, scripts):
    for dir in dir_list:
        for root, dirs, files in os.walk(os.path.join(directory, dir)):
            for script_name in scripts:
                script_path = os.path.join(root, script_name)
                if script_name in files and os.path.isfile(script_path):
                    print(f"Running {script_path}...")
                    os.chdir(root)
                    print(os.getcwd())
                    subprocess.run(['python3', script_path], check=True)
                # else:
                #     print(f"Script {script_name} not found in {root}, skipping...")

if __name__ == "__main__":
    run_scripts_in_directory(project_root, scripts_to_run.keys())
