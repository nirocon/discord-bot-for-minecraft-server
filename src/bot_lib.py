import subprocess


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
