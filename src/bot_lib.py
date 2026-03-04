import subprocess
import os
import datetime

# ログディレクトリの準備
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIR = os.path.join(ROOT_DIR, '.bin', 'log')
# ログ用ディレクトリ作成
os.makedirs(LOG_DIR, exist_ok=True)

def run_logged(command, capture_output=False, **kwargs):
    """サブプロセスを実行し、stdout/stderr をログディレクトリに残す

    Args:
        command: 実行するコマンド文字列
        capture_output: True なら出力をキャプチャして戻り値の result に含める
        kwargs: subprocess.run に渡す追加引数
    Returns:
        subprocess.CompletedProcess
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_DIR, f"{timestamp}.log")
    if capture_output:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, **kwargs)
        # ログへ書き出し
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"$ {command}\n")
            if result.stdout:
                f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
        return result
    else:
        with open(log_path, 'a', encoding='utf-8') as f:
            result = subprocess.run(command, shell=True, stdout=f, stderr=subprocess.STDOUT, **kwargs)
        return result



def get_screen_session(minecraft_controll_account: str):
    """screenセッションを取得する関数"""
    try:
        command = f"sudo -u {minecraft_controll_account} screen -ls"
        process_return = subprocess.run(command, check=True, capture_output=True, shell=True)
        output = process_return.stdout.decode('utf-8')
        return output
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:  # screenが起動していないとき
            return ""
        else:
            raise
    except Exception as e:
        raise


def check_screen_session(minecraft_controll_account: str, session_name: str):
    """screenセッションを確認する関数"""
    session = get_screen_session(minecraft_controll_account)
    return session_name in session
