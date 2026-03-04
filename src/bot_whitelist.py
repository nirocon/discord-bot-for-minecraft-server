import subprocess
import json
from bot_lib import check_screen_session, run_logged


def whitelist_add(
    minecraft_controll_account: str,
    session_name: str,
    start_server_command: str,
    username: str
):
    """ホワイトリストに追加する関数"""
    try:
        if not check_screen_session(minecraft_controll_account, session_name):
            return f"Minecraftサーバーは起動していません\n`/{start_server_command}`で起動してください"

        command = f"sudo -u {minecraft_controll_account} screen -S {session_name} -p 0 -X stuff 'whitelist add {username}\n'"
        result = run_logged(command, check=True)
        if result.returncode == 0:
            return f"{username}をホワイトリストに追加しました!"
        else:
            return "ホワイトリスト追加時にエラー"
    except Exception as e:
        print(e)
        return "ホワイトリスト追加時にエラー"


def whitelist_remove(
    minecraft_controll_account: str,
    session_name: str,
    start_server_command: str,
    username: str
):
    """ホワイトリストから削除する関数"""
    try:
        if not check_screen_session(minecraft_controll_account, session_name):
            return f"Minecraftサーバーは起動していません\n`/{start_server_command}`で起動してください"

        command = f"sudo -u {minecraft_controll_account} screen -S {session_name} -p 0 -X stuff 'whitelist remove {username}\n'"
        result = run_logged(command, check=True)
        if result.returncode == 0:
            return f"{username}をホワイトリストから削除しました!"
        else:
            return "ホワイトリスト削除時にエラー"
    except Exception as e:
        print(e)
        return "ホワイトリスト削除時にエラー"


def whitelist_list(
    minecraft_controll_account: str,
    minecraft_server_dir_path: str
):
    """ホワイトリストを表示する関数"""
    try:
        # キャプチャしつつログにも残す
        result = run_logged(f"sudo -u {minecraft_controll_account} cat {minecraft_server_dir_path}/allowlist.json", capture_output=True)
        whitelist_raw = result.stdout if result.stdout is not None else ""
        whitelist = json.loads(whitelist_raw)

        # whitelistが空の場合
        if not whitelist:
            return "ホワイトリストに追加されているユーザーはありません"

        # whitelistにユーザーがいる場合
        names = ""
        for user in whitelist:
            names += f"{user['name']}\n"
        return f"ホワイトリストに追加されているユーザー\n\n{names}"
    except json.JSONDecodeError as e:
        print(e)
        return "ホワイトリストファイルが壊れています"
    except Exception as e:
        print(e)
        return f"ホワイトリスト表示時にエラー"
