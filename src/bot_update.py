import subprocess
import os
import tempfile
import shutil
from bot_backup import back_up_minecraft_server


def update_minecraft_server(
    minecraft_controll_account: str,
    session_name: str,
    server_path: str,
    server_version: str,
    create_backup: bool = True,
    backup_path: str = None,
    backup_name: str = None,
    server_url_template: str = None,
) -> str:
    """
    Minecraftサーバーをアップデートする関数
    
    Args:
        minecraft_controll_account: マイクラサーバーを実行しているユーザー名
        session_name: screenセッション名
        server_path: サーバーのパス
        server_version: サーバーバージョン（URLテンプレートに使用）
        create_backup: アップデート前にバックアップを作成するか（デフォルト: True）
        backup_path: バックアップ先のパス（create_backup=Trueの場合に使用）
        backup_name: バックアップファイル名
        server_url_template: サーバーダウンロードURLテンプレート（デフォルト: Bedrock公式）
    
    Returns:
        処理結果のメッセージ
    """
    try:
        returned_message = ""
        
        # デフォルトURLテンプレート（Minecraft Bedrock Edition）
        if server_url_template is None:
            server_url_template = f"https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-{server_version}.zip"
        
        # バックアップを実行
        if create_backup:
            if backup_path is None:
                returned_message += "バックアップパスが指定されていません。\n"
                return returned_message
            
            print("アップデート前にバックアップを作成します...")
            returned_message += "アップデート前にバックアップを作成します...\n"
            backup_result = back_up_minecraft_server(
                minecraft_controll_account=minecraft_controll_account,
                session_name=session_name,
                server_path=server_path,
                backup_path=backup_path,
                backup_name=backup_name,
            )
            returned_message += backup_result
        
        # 一時ディレクトリにアーカイブをダウンロード
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file = os.path.join(temp_dir, f"bedrock-server-{server_version}.zip")
            
            # wgetでダウンロード
            print(f"サーバーパッケージをダウンロード中 ({server_version})...")
            download_command = f"sudo -u {minecraft_controll_account} wget -O {zip_file} '{server_url_template}'"
            result = subprocess.run(download_command, shell=True, capture_output=True)
            
            if result.returncode != 0:
                returned_message += "サーバーパッケージのダウンロードに失敗しました。バージョンを確認してください。\n"
                return returned_message
            
            # ファイルが存在するか確認
            check_command = f"sudo -u {minecraft_controll_account} test -f {zip_file}"
            if subprocess.run(check_command, shell=True).returncode != 0:
                returned_message += "ダウンロードされたファイルが見つかりません。サーバー管理者またはボット開発者に確認してください。\n"
                return returned_message
            
            # 展開ディレクトリ
            extracted_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extracted_dir, exist_ok=True)
            
            # unzipで展開
            print("サーバーパッケージを展開中...")
            extract_command = f"sudo -u {minecraft_controll_account} unzip -q -o {zip_file} -d {extracted_dir}"
            if subprocess.run(extract_command, shell=True).returncode != 0:
                returned_message += "サーバーパッケージの展開に失敗しました。サーバー管理者またはボット開発者に確認してください。\n"
                return returned_message
            
            # 旧サーバーをリネーム
            old_server_path = f"{server_path}-old"
            print(f"旧サーバーを {old_server_path} にバックアップ中...")
            
            # 既に-oldが存在する場合は削除
            remove_old_command = f"sudo -u {minecraft_controll_account} rm -rf {old_server_path}"
            subprocess.run(remove_old_command, shell=True)
            
            # サーバーフォルダをリネーム
            rename_command = f"sudo -u {minecraft_controll_account} mv {server_path} {old_server_path}"
            if subprocess.run(rename_command, shell=True).returncode != 0:
                returned_message += "旧サーバーのリネームに失敗しました。サーバー管理者またはボット開発者に確認してください。\n"
                return returned_message
            
            # 新しいサーバーフォルダを作成
            mkdir_command = f"sudo -u {minecraft_controll_account} mkdir -p {server_path}"
            if subprocess.run(mkdir_command, shell=True).returncode != 0:
                returned_message += "新しいサーバーフォルダの作成に失敗しました。サーバー管理者またはボット開発者に確認してください。\n"
                return returned_message
            
            # 展開したファイルを新しいサーバーフォルダにコピー
            print("新しいサーバーパッケージをインストール中...")
            copy_extracted_command = f"sudo -u {minecraft_controll_account} cp -r {extracted_dir}/* {server_path}/"
            if subprocess.run(copy_extracted_command, shell=True).returncode != 0:
                returned_message += "新しいパッケージのコピーに失敗しました。サーバー管理者またはボット開発者に確認してください。\n"
                return returned_message
            
            # 旧サーバーから設定ファイルと世界データをコピー
            returned_message += "設定ファイルと世界データをコピー中...\n"
            
            files_to_copy = [
                "server.properties",
                "permissions.json",
                "allowlist.json",
            ]
            
            for file_name in files_to_copy:
                old_file = os.path.join(old_server_path, file_name)
                new_file = os.path.join(server_path, file_name)
                copy_command = f"sudo -u {minecraft_controll_account} cp {old_file} {new_file}"
                # ファイルが存在しない場合はスキップ
                check_file_command = f"sudo -u {minecraft_controll_account} test -f {old_file}"
                if subprocess.run(check_file_command, shell=True).returncode == 0:
                    subprocess.run(copy_command, shell=True)
            
            # worldsディレクトリをコピー
            old_worlds = os.path.join(old_server_path, "worlds")
            new_worlds = os.path.join(server_path, "worlds")
            copy_worlds_command = f"sudo -u {minecraft_controll_account} cp -r {old_worlds} {new_worlds}"
            check_worlds_command = f"sudo -u {minecraft_controll_account} test -d {old_worlds}"
            if subprocess.run(check_worlds_command, shell=True).returncode == 0:
                if subprocess.run(copy_worlds_command, shell=True).returncode != 0:
                    returned_message += "ワールドデータのコピーに失敗しました。サーバー管理者またはボット開発者に確認してください。\n"
                    return returned_message
        
        returned_message += f"サーバーアップデート完了！ (バージョン: {server_version})\n"
        return returned_message
        
    except Exception as e:
        print(e)
        returned_message += f"アップデート中にエラーが発生しました。サーバー管理者またはボット開発者に確認してください。\n"
        return returned_message
