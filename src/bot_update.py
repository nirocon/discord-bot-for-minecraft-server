import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from bot_backup import back_up_minecraft_server
from bot_lib import check_screen_session

BOT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "bot.config"

PACK_ROOTS = {
    "behavior_packs",
    "resource_packs",
    "development_behavior_packs",
    "development_resource_packs",
}


def _load_update_config(server):
    with BOT_CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
        config = json.load(file)

    update = config.get("update")
    if not isinstance(update, dict):
        raise ValueError("bot.config: update を指定してください。")

    unknown = set(update) - {"packs", "settings"}
    if unknown:
        raise ValueError(f"bot.config: 未対応の項目があります: {sorted(unknown)}")

    result = {}

    for category in ("packs", "settings"):
        entries = update.get(category)
        if not isinstance(entries, list):
            raise ValueError(f"bot.config: {category} は配列で指定してください。")

        paths = []
        seen = set()

        for entry in entries:
            if not isinstance(entry, str) or not entry.strip():
                raise ValueError(f"bot.config: {category} に空のパスがあります。")

            relative = Path(entry)

            if (
                relative.is_absolute()
                or ".." in relative.parts
                or "\\" in entry
                or ":" in entry
                or not relative.parts
            ):
                raise ValueError(
                    f"bot.config: 相対パスを / 区切りで指定してください: {entry}"
                )

            source = server / relative

            # シンボリックリンクによるサーバー外への参照を防ぐ。
            if not source.resolve().is_relative_to(server.resolve()):
                raise ValueError(f"bot.config: サーバー外を参照しています: {entry}")

            if category == "packs":
                if len(relative.parts) != 2 or relative.parts[0] not in PACK_ROOTS:
                    raise ValueError(
                        f"bot.config: パックはルート/パック名で指定してください: {entry}"
                    )
                if not source.is_dir() or not (source / "manifest.json").is_file():
                    raise ValueError(f"bot.config: パックが見つかりません: {entry}")
            else:
                # 実行ファイルや標準パックを設定として上書きしない。
                if not (
                    relative.as_posix()
                    in {
                        "server.properties",
                        "permissions.json",
                        "allowlist.json",
                        "packetlimitconfig.json",
                    }
                    or (relative.parts[0] == "config" and len(relative.parts) >= 2)
                ):
                    raise ValueError(
                        f"bot.config: 設定ファイルとして指定できません: {entry}"
                    )
                if not source.is_file():
                    raise ValueError(
                        f"bot.config: 設定ファイルが見つかりません: {entry}"
                    )

            normalized = relative.as_posix()
            if normalized in seen:
                raise ValueError(f"bot.config: 指定が重複しています: {entry}")
            seen.add(normalized)

            paths.append(relative)

        result[category] = paths

    return result


def _run_as(account, *args):
    """シェルを経由せず、サーバー実行ユーザーとして実行する。"""
    result = subprocess.run(
        ["sudo", "-u", account, "--", *map(str, args)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{args[0]} が失敗しました: {detail or '詳細なし'}")
    return result


def _copy_as(account, source, destination):
    """ディレクトリのコピー先は、存在しない場所を指定する。"""
    _run_as(account, "mkdir", "-p", destination.parent)
    _run_as(account, "cp", "-a", source, destination)


def _read_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def _validate_world_packs(server):
    """ワールドが要求するパックと依存パックを検証する。"""
    manifests = {}

    # サーバー共通パック
    pack_roots = [
        server / "behavior_packs",
        server / "resource_packs",
        server / "development_behavior_packs",
        server / "development_resource_packs",
    ]

    worlds = server / "worlds"
    if not worlds.is_dir():
        raise RuntimeError("移行先に worlds フォルダーがありません。")

    world_dirs = [
        world
        for world in worlds.iterdir()
        if world.is_dir() and (world / "level.dat").is_file()
    ]
    if not world_dirs:
        raise RuntimeError("移行先にワールドが見つかりません。")

    def collect(roots):
        result = {}
        for root in roots:
            if not root.is_dir():
                continue
            for path in root.glob("*/manifest.json"):
                manifest = _read_json(path)
                header = manifest["header"]
                key = (
                    header["uuid"].lower(),
                    tuple(header["version"]),
                )
                result[key] = (manifest, path.parent)
        return result

    manifests.update(collect(pack_roots))

    for world in world_dirs:
        # ワールド内に配置されたパックにも対応
        available = dict(manifests)
        available.update(
            collect(
                [
                    world / "behavior_packs",
                    world / "resource_packs",
                ]
            )
        )
        checked = set()

        def check_pack(pack_id, version, subpack=None):
            key = (pack_id.lower(), tuple(version))
            if key not in available:
                raise RuntimeError(
                    f"{world.name}: パック不足 UUID={pack_id}, version={list(version)}"
                )

            manifest, folder = available[key]

            if subpack:
                declared = {
                    entry["folder_name"] for entry in manifest.get("subpacks", [])
                }
                if (
                    subpack not in declared
                    or not (folder / "subpacks" / subpack).is_dir()
                ):
                    raise RuntimeError(f"{world.name}: サブパック不足 {subpack}")

            if key in checked:
                return
            checked.add(key)

            for dependency in manifest.get("dependencies", []):
                # UUIDで参照する別パックの存在を確認。
                # @minecraft/server等のAPI互換性は起動時に確認。
                if "uuid" in dependency:
                    check_pack(
                        dependency["uuid"],
                        dependency["version"],
                    )

        for name in (
            "world_behavior_packs.json",
            "world_resource_packs.json",
        ):
            registration = world / name
            if not registration.is_file():
                continue
            for entry in _read_json(registration):
                check_pack(
                    entry["pack_id"],
                    entry["version"],
                    entry.get("subpack"),
                )


def update_minecraft_server(
    minecraft_controll_account: str,
    session_name: str,
    server_path: str,
    server_version: str,
    create_backup: bool = True,
    backup_path: str = None,
    backup_name: str = None,
) -> str:
    account = minecraft_controll_account
    messages = []
    stage = None
    retired = None

    try:
        if check_screen_session(account, session_name):
            return "Minecraftサーバーが起動中です。先にサーバーを停止してください。\n"

        if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", server_version):
            return "バージョンは N.N.N.N の形式で指定してください。\n"

        server = Path(server_path).resolve()
        if not server.is_dir() or server == Path(server.anchor):
            return "サーバーフォルダーの指定が不正です。\n"

        update_config = _load_update_config(server)

        # 既存のバックアップ関数はシェルコマンドを使うため、
        # 渡すパス・ユーザー名をここで引用します。
        if create_backup:
            if not backup_path:
                return "バックアップ先が指定されていません。\n"

            result = back_up_minecraft_server(
                minecraft_controll_account=account,
                session_name=session_name,
                server_path=str(server),
                backup_path=backup_path,
                backup_name=backup_name,
            )

            messages.append(result)

            # bot_backup.pyを変更しないため、現在の成功文で判定。
            if "バックアップを作成しました！" not in result:
                messages.append(
                    "バックアップの成功を確認できないため、更新を中止しました。\n"
                )
                return "".join(messages)

        # 一意な作業フォルダーを、正式フォルダーと同じ場所に作成。
        result = _run_as(
            account,
            "mktemp",
            "-d",
            str(server.parent / f"{server.name}-new-XXXXXX"),
        )
        stage = Path(result.stdout.strip()).resolve()

        if stage.parent != server.parent:
            raise RuntimeError("作業フォルダーの場所が不正です。")

        # 検証時にボットから読み取れるようにする。
        _run_as(account, "chmod", "755", stage)

        url = (
            "https://www.minecraft.net/bedrockdedicatedserver/"
            f"bin-linux/bedrock-server-{server_version}.zip"
        )

        with tempfile.TemporaryDirectory() as temporary:
            # sudo先のユーザーがダウンロードできるようにする。
            os.chmod(temporary, 0o777)
            archive = Path(temporary) / "server.zip"

            _run_as(account, "wget", "-O", archive, url)
            _run_as(account, "unzip", "-q", archive, "-d", stage)

        if not (stage / "bedrock_server").is_file():
            raise RuntimeError("展開したパッケージに bedrock_server がありません。")

        # 新パッケージに worlds が含まれていた場合も、
        # worlds/worlds という入れ子を作らずに移行。
        packaged_worlds = stage / "worlds"
        if packaged_worlds.exists():
            _run_as(
                account,
                "mv",
                packaged_worlds,
                stage / "_package_worlds",
            )

        old_worlds = server / "worlds"
        if not old_worlds.is_dir():
            raise RuntimeError("旧サーバーに worlds がありません。")
        _copy_as(account, old_worlds, stage / "worlds")

        # 指定した設定ファイルを移行する。
        for relative in update_config["settings"]:
            source = server / relative
            destination = stage / relative

            if destination.exists() and not destination.is_file():
                raise RuntimeError(
                    f"設定ファイルのコピー先がファイルではありません: {relative}"
                )

            _copy_as(account, source, destination)
            messages.append(f"設定を引き継ぎました: {relative}\n")

        # 指定した追加パックを移行する。
        for relative in update_config["packs"]:
            source = server / relative
            destination = stage / relative

            if destination.exists():
                raise RuntimeError(
                    f"新版パッケージと追加パックが競合します: {relative}"
                )

            _copy_as(account, source, destination)
            messages.append(f"パックを引き継ぎました: {relative}\n")

        # config/defaultは新版を使用。
        # スクリプトUUID別の独自設定フォルダーを引き継ぐ。
        old_config = server / "config"
        if old_config.is_dir():
            for source in old_config.iterdir():
                if not source.is_dir() or source.name == "default":
                    continue

                destination = stage / "config" / source.name
                if destination.exists():
                    raise RuntimeError(f"独自configが新版と競合します: {source.name}")
                _copy_as(account, source, destination)

        _validate_world_packs(stage)

        # default設定は旧版も保存し、手動比較できるようにする。
        old_default = server / "config" / "default"
        if old_default.is_dir():
            _copy_as(
                account,
                old_default,
                stage / "_previous_config_default",
            )
            messages.append(
                "旧config/defaultは _previous_config_default に"
                "保存しました。独自変更がある場合は比較してください。\n"
            )

        # 準備中にサーバーが起動していないか再確認。
        if check_screen_session(account, session_name):
            raise RuntimeError(
                "準備中にサーバーが起動したため、切り替えを中止しました。"
            )

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        retired = server.with_name(f"{server.name}-old-{stamp}")
        if retired.exists():
            raise RuntimeError("退避先がすでに存在します。")

        _run_as(account, "mv", server, retired)

        try:
            _run_as(account, "mv", stage, server)
        except Exception:
            # 切り替えに失敗した場合は旧版を元に戻す。
            if not server.exists():
                _run_as(account, "mv", retired, server)
            raise

        stage = None
        messages.append(
            f"サーバー更新とパック移行が完了しました: {server_version}\n"
            f"旧サーバーの保存先: {retired}\n"
            "起動後にログとアドオンの動作を確認してください。\n"
        )

    except Exception as error:
        messages.append(f"更新を中止しました: {error}\n")
        if stage is not None:
            messages.append(f"確認用の作業フォルダーを残しています: {stage}\n")
        if retired is not None and retired.exists():
            messages.append(f"旧サーバーの保存先: {retired}\n")

    return "".join(messages)
