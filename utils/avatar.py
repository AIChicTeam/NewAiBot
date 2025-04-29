# avatar.py
import asyncio
import os
import shutil
import paramiko

from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from utils.runpod_start import ensure_pod_ready
from database import decrease_credits, set_avatar_generated, get_payment_status, count_photos, check_if_avatar_exists
from keyboards.main_menu import get_main_menu

router = Router()

# === CONFIG for remote training ===
ssh_host = "104.129.132.157"
ssh_port = 11368
ssh_username = "root"
ssh_password = "your_ssh_password"  # заменишь здесь на свой пароль
remote_upload_folder = "/workspace/input_files"
remote_lora_folder = "/workspace/output_lora"
training_command = "bash /workspace/start_training.sh"


def prepare_user_folder(user_id: int) -> str:
    return os.path.abspath(f"user_photos/{user_id}")


async def generate_avatar_task(user_id: int, bot: Bot):
    local_folder = prepare_user_folder(user_id)

    await bot.send_message(user_id, "🤖 Your avatar is being generated... Please wait ⏳")

    # 1. Ensure pod is ready
    ensure_pod_ready()

    # 2. Connect to SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)
    sftp = ssh.open_sftp()

    # 3. Upload files
    for filename in os.listdir(local_folder):
        local_path = os.path.join(local_folder, filename)
        remote_path = os.path.join(remote_upload_folder, filename)
        sftp.put(local_path, remote_path)

    # 4. Run training
    stdin, stdout, stderr = ssh.exec_command(training_command)
    for line in iter(stdout.readline, ""):
        print(line, end="")
    stdout.channel.recv_exit_status()

    # 5. Download LoRA results
    result_path = f"user_results/{user_id}"
    os.makedirs(result_path, exist_ok=True)
    for filename in sftp.listdir(remote_lora_folder):
        remote_file = os.path.join(remote_lora_folder, filename)
        local_file = os.path.join(result_path, filename)
        sftp.get(remote_file, local_file)

    # 6. Cleanup
    for filename in sftp.listdir(remote_upload_folder):
        sftp.remove(os.path.join(remote_upload_folder, filename))
    for filename in sftp.listdir(remote_lora_folder):
        sftp.remove(os.path.join(remote_lora_folder, filename))
    shutil.rmtree(local_folder)

    sftp.close()
    ssh.close()

    # 7. Notify user
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎨 Choose Style", callback_data="select_style")]
    ])

    await bot.send_message(
        user_id,
        "✅ Your AI avatar is ready! Click below to view it (or wait for the next update).",
        reply_markup=kb
    )

    if not await decrease_credits(user_id):
        await bot.send_message(user_id, "⚠️ You’ve used all 100 generations. Please pay again to continue.")
