import subprocess
import time
from bot_lib import check_screen_session, run_logged
import shlex

def back_up_minecraft_server(
    minecraft_controll_account: str,
    session_name: str,
    server_path: str,
    backup_path: str,
    backup_name: str = None,
) -> str:
    """Minecraftサーバーのバックアップを作成する関数"""
    try:
        def shell_command(*args):
            return shlex.join([str(arg) for arg in args])
        returned_message = ""
        # サーバーの起動を確認
        if check_screen_session(minecraft_controll_account, session_name):
            returned_message += "サーバーが起動中のため、バックアップを作成する前にサーバーを停止してください。\n"
            return returned_message
        
        # マイクラサーバーディレクトリが存在するか確認
        command_check_dir = shell_command(
            "sudo", "-u", minecraft_controll_account,
            "test", "-d", server_path,
        )
        process_return = run_logged(command_check_dir)
        if process_return.returncode != 0:
            returned_message += "マイクラサーバーディレクトリが存在しません。サーバー管理者に確認してください。\n"
            return returned_message
        
        # バックアップの保存先のディレクトリが存在するか確認
        command_check_dir = shell_command(
            "sudo", "-u", minecraft_controll_account,
            "test", "-d", backup_path,
        )
        process_return = run_logged(command_check_dir)
        if process_return.returncode != 0:
            returned_message += f"バックアップの保存先のディレクトリが存在しません。ディレクトリを新規作成して保存します。\n"
            command_create_dir = f"sudo -u {minecraft_controll_account} mkdir -p {backup_path}"
            run_logged(command_create_dir, check=True)

        # 日時を取得、バックアップファイル名を作成
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if backup_name is None:
            # 自動のバックアップファイル名を使用
            backup_path = f"{backup_path}/{server_path.split('/')[-1]}_backup_{timestamp}.tar.gz"
        elif not backup_name.endswith(".tar.gz"):
            # 拡張子を付けたバックアップファイル名を使用
            backup_path = f"{backup_path}/{backup_name}.tar.gz"
        else:
            # 指定されたバックアップファイル名を使用
            backup_path = f"{backup_path}/{backup_name}"
        
        # バックアップを作成するコマンドを実行
        print(f"バックアップ({backup_path})を作成中...")
        command = shell_command(
            "sudo", "-u", minecraft_controll_account,
            "tar", "-zcf", backup_path, server_path,
        )
        run_logged(command, check=True)  # tar の出力はログに残る

        returned_message += f"バックアップを作成しました！\n"
        return returned_message
    except Exception as e:
        print(e)
        returned_message += "バックアップ作成時にエラーが発生しました。\n"
        return returned_message