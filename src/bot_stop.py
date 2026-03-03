import subprocess
from bot_lib import check_screen_session


def stop_minecraft_server(
    minecraft_controll_account: str,
    session_name: str,
    start_server_command: str
):
    """マイクラサーバーを停止する関数"""
    try:
        if not check_screen_session(minecraft_controll_account, session_name):
            return f"Minecraftサーバーは起動していません\n`/{start_server_command}`で起動してください"

        command = f"sudo -u {minecraft_controll_account} screen -S {session_name} -p 0 -X stuff 'stop\n'"
        subprocess.run(command, check=True, shell=True)
        return "Minecraftサーバーを停止しました!"
    except Exception as e:
        print(e)
        return "サーバー停止時にエラー"
