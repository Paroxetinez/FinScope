from flask import Flask
from flask_migrate import Migrate, upgrade, init, stamp
from app import create_app, db
import os
import datetime
import sqlite3
import shutil

app = create_app()
migrate = Migrate(app, db)


def backup_database():
    """备份数据库"""
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'db_backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # SQLite数据库文件路径
        db_path = 'instance/users.db'
        backup_path = f'{backup_dir}/users_{timestamp}.db'

        # 复制数据库文件作为备份
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            print(f"数据库已备份到: {backup_path}")
            return backup_path
        else:
            print("数据库文件不存在")
            return None
    except Exception as e:
        print(f"备份失败: {str(e)}")
        return None


def clean_alembic_version():
    """清理数据库中的版本记录"""
    try:
        with app.app_context():
            # 连接到 SQLite 数据库
            db_path = 'instance/users.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 删除 alembic_version 表（如果存在）
            cursor.execute("DROP TABLE IF EXISTS alembic_version")
            conn.commit()
            conn.close()
            print("已清理数据库版本记录")
            return True
    except Exception as e:
        print(f"清理版本记录失败: {str(e)}")
        return False


def reset_migrations():
    """重置迁移环境"""
    try:
        # 1. 清理数据库版本记录
        if not clean_alembic_version():
            raise Exception("清理数据库版本记录失败")

        # 2. 删除现有的迁移文件夹
        if os.path.exists('migrations'):
            shutil.rmtree('migrations')
        print("已清理旧的迁移文件")

        # 3. 重新初始化迁移
        with app.app_context():
            # 初始化迁移环境
            init()
            print("迁移环境初始化完成")

            # 创建初始迁移
            os.system('flask db migrate -m "initial migration"')
            print("创建初始迁移完成")

            # 标记数据库为当前版本
            stamp()
            print("数据库版本已更新")

        return True
    except Exception as e:
        print(f"重置迁移失败: {str(e)}")
        return False


def safe_migrate():
    """安全的数据库迁移"""
    backup_path = None  # 初始化 backup_path
    try:
        # 1. 备份数据库
        backup_path = backup_database()
        if not backup_path:
            raise Exception("数据库备份失败")

        # 2. 重置迁移环境
        if not reset_migrations():
            raise Exception("重置迁移环境失败")

        # 3. 创建新的迁移脚本
        print("创建迁移脚本...")
        os.system("flask db migrate -m 'auto migration'")

        # 4. 应用迁移
        print("应用迁移...")
        with app.app_context():
            upgrade()

        print("数据库迁移成功完成！")
        return True

    except Exception as e:
        print(f"迁移失败: {str(e)}")
        if backup_path and os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, 'instance/users.db')
                print("已恢复到备份版本")
            except Exception as restore_error:
                print(f"恢复备份失败: {str(restore_error)}")
        return False


def verify_migration():
    """验证迁移结果"""
    try:
        with app.app_context():
            # 验证所有模型是否可以正常查询
            from app.models import User, Conversation, Message, RelatedQuestion, UserPreferences

            User.query.first()
            Conversation.query.first()
            Message.query.first()
            RelatedQuestion.query.first()
            UserPreferences.query.first()

            print("数据库结构验证成功")
            return True
    except Exception as e:
        print(f"数据库验证失败: {str(e)}")
        return False


if __name__ == "__main__":
    if safe_migrate():
        if verify_migration():
            print("数据库更新成功完成")
        else:
            print("数据库更新完成，但验证失败")
    else:
        print("数据库更新失败")
