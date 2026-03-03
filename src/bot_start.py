import subprocess
from bot_lib import check_screen_session


def start_minecraft_server(
    minecraft_controll_account: str,
    minecraft_server_dir_path: str,
    session_name: str
):
    """マイクラサーバーを起動する関数"""
    try:
        if check_screen_session(minecraft_controll_account, session_name):
            return "Minecraftサーバーはすでに起動しています"

        command = f"sudo -u {minecraft_controll_account} bash -c 'cd {minecraft_server_dir_path} && LD_LIBRARY_PATH=. screen -dmS {session_name} ./bedrock_server'"
        subprocess.run(command, check=True, shell=True)
        return "Minecraftサーバーを起動しました!"
    except Exception as e:
        print(e)
        return "サーバー起動時にエラー"
