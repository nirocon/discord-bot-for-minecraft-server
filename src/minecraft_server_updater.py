import subprocess
import time
import bot;

def back_up_minecraft_server(server_path: str, backup_path: str, backup_name: str = None) -> str:
    """Minecraftサーバーのバックアップを作成する関数"""
    try:
        returned_message = ""
        # サーバーの起動を確認
        if bot.check_screen_session(bot.SESSION_NAME):
            returned_message += "サーバーが起動中のため、バックアップを作成する前にサーバーを停止してください。\n"
            return returned_message
        
        # バックアップするディレクトリが存在するか確認
        command_check_dir = f"sudo -u {bot.MINECRAFT_CONTROLL_ACCOUNT} test -d {server_path}"
        process_return = subprocess.run(command_check_dir, shell=True)
        if process_return.returncode != 0:
            returned_message += "バックアップするサーバーディレクトリが存在しません。パスを確認してください。\n"
            return returned_message
        
        # バックアップ先のディレクトリが存在するか確認
        command_check_dir = f"sudo -u {bot.MINECRAFT_CONTROLL_ACCOUNT} test -d {backup_path}"
        process_return = subprocess.run(command_check_dir, shell=True)
        if process_return.returncode != 0:
            returned_message += f"バックアップ先のディレクトリが存在しません。ディレクトリを作成して保存します。\n"
            command_create_dir = f"sudo -u {bot.MINECRAFT_CONTROLL_ACCOUNT} mkdir -p {backup_path}"
            subprocess.run(command_create_dir, check=True, shell=True)

        # 日時を取得、バックアップファイル名を作成
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if backup_name is None:
            # 自動のバックアップファイル名を使用
            backup_path = f"{backup_path}/{server_path.strip('/')[-1]}_backup_{timestamp}.tar.gz"
        elif not backup_name.endswith(".tar.gz"):
            # 拡張子を付けたバックアップファイル名を使用
            backup_path = f"{backup_path}/{backup_name}.tar.gz"
        else:
            # 指定されたバックアップファイル名を使用
            backup_path = f"{backup_path}/{backup_name}"
        
        # バックアップを作成するコマンドを実行
        command = f"sudo -u {bot.MINECRAFT_CONTROLL_ACCOUNT} tar -zcvf {backup_path} {server_path}"
        process = subprocess.Popen(command, check=True, shell=True)

        process.wait() # コマンドの完了を待機

        returned_message += f"バックアップを作成しました！\n"
        return returned_message
    except Exception as e:
        print(e)
        returned_message += "バックアップ作成時にエラーが発生しました。\n"
        return returned_message