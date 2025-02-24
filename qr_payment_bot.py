import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from urllib.parse import quote
import requests
from datetime import datetime
import asyncio  # Thêm import asyncio

# Load environment variables
load_dotenv()

# Configuration from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BANK_ID = os.getenv('BANK_ID', '970436')
ACCOUNT_NO = os.getenv('ACCOUNT_NO')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME')

# Thêm hằng số cho ROLE_ID
CUSTOMER_ROLE_ID = 1334194617322831935

# Thêm hằng số cho LOG_CHANNEL_ID
LOG_CHANNEL_ID = 1336368295363874909


def generate_vietqr_content(amount: float, message: str = ""):
    """
    Generate VietQR content with proper URL encoding
    """
    # Ensure all components are properly encoded
    encoded_account_name = quote(ACCOUNT_NAME)
    encoded_message = quote(message)

    # Format according to VietQR standard
    qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact.png"
    qr_url += f"?amount={int(amount)}"
    if message:
        qr_url += f"&addInfo={encoded_message}"
    qr_url += f"&accountName={encoded_account_name}"

    print(f"Generated QR URL: {qr_url}")  # For debugging
    return qr_url


class QRPaymentBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        try:
            print("Synchronizing commands...")
            await self.tree.sync()
            print("Command synchronization successful!")
        except Exception as e:
            print(f"Error synchronizing commands: {e}")


bot = QRPaymentBot()


@bot.tree.command(name="thanhtoan", description="Tạo mã QR thanh toán ngân hàng")
@app_commands.describe(
    amount="Số lượng key cần thanh toán",
)
async def generate_qr(
    interaction: discord.Interaction,
    amount: int,
):
    try:
        # Validate key amount
        if amount < 5:
            await interaction.response.send_message("❌ Số lượng key phải lớn hơn hoặc bằng 5!")
            return

        # Calculate price based on quantity
        total_price = 250000 * amount if amount >= 10 else 275000 * amount

        await interaction.response.defer()

        # Generate VietQR URL with encoded parameters
        message = f"{interaction.user.name}"
        qr_url = generate_vietqr_content(total_price, message)

        # Create embed with payment information
        embed = discord.Embed(
            title="💳 Thông tin thanh toán",
            description=f"**Số lượng key:** {amount} key\n**Đơn giá:** {250000 if amount >= 10 else 275000:,} VNĐ/key",
            color=0x00ff00  # Màu xanh lá cây tươi sáng
        )

        # Thông tin ngân hàng
        embed.add_field(
            name="🏦 Thông tin tài khoản",
            value=f"```\nNgân hàng: BIDV\nChủ TK: {ACCOUNT_NAME}\nSố TK: {ACCOUNT_NO}\n```",
            inline=False
        )

        # Thông tin thanh toán
        embed.add_field(
            name="💰 Chi tiết thanh toán",
            value=f"```\nTổng tiền: {total_price:,} VNĐ\nNội dung CK: {message}\n```",
            inline=False
        )

        # Set the encoded QR URL
        try:
            embed.set_image(url=qr_url)
        except Exception as e:
            print(f"Error setting image URL: {e}")
            await interaction.followup.send("❌ Không thể tạo mã QR. Vui lòng thử lại sau.")
            return

        embed.set_footer(text=f"Yêu cầu bởi: {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    except ValueError:
        await interaction.followup.send('❌ Vui lòng nhập một số hợp lệ.')
    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send('❌ Có lỗi xảy ra. Vui lòng thử lại sau.')


@bot.tree.command(name="giahan", description="Tạo mã QR gia hạn")
@app_commands.describe(
    amount="Số lượng key cần gia hạn",
)
async def extend_subscription(
    interaction: discord.Interaction,
    amount: int,
):
    try:
        # Validate key amount
        if amount <= 0:
            await interaction.response.send_message("❌ Số lượng key phải lớn hơn 0!")
            return

        # Calculate price based on quantity
        total_price = 250000 * amount if amount >= 10 else 275000 * amount

        await interaction.response.defer()

        # Generate VietQR URL with encoded parameters
        message = f"Gia han - {interaction.user.name}"
        qr_url = generate_vietqr_content(total_price, message)

        # Create embed with payment information
        embed = discord.Embed(
            title="💳 Thông tin gia hạn",
            description=f"**Số lượng key:** {amount} key\n**Đơn giá:** {250000 if amount >= 10 else 275000:,} VNĐ/key",
            color=0x00ff00
        )

        # Thông tin ngân hàng
        embed.add_field(
            name="🏦 Thông tin tài khoản",
            value=f"```\nNgân hàng: BIDV\nChủ TK: {ACCOUNT_NAME}\nSố TK: {ACCOUNT_NO}\n```",
            inline=False
        )

        # Thông tin thanh toán
        embed.add_field(
            name="💰 Chi tiết thanh toán",
            value=f"```\nTổng tiền: {total_price:,} VNĐ\nNội dung CK: {message}\n```",
            inline=False
        )

        # Set the encoded QR URL
        try:
            embed.set_image(url=qr_url)
        except Exception as e:
            print(f"Error setting image URL: {e}")
            await interaction.followup.send("❌ Không thể tạo mã QR. Vui lòng thử lại sau.")
            return

        embed.set_footer(text=f"Yêu cầu bởi: {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    except ValueError:
        await interaction.followup.send('❌ Vui lòng nhập một số hợp lệ.')
    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send('❌ Có lỗi xảy ra. Vui lòng thử lại sau.')


@bot.tree.command(name="sendmsg", description="Gửi tin nhắn trực tiếp đến user")
@app_commands.describe(
    user="Người dùng cần gửi tin nhắn",
    message="Nội dung tin nhắn cần gửi"
)
async def send_direct_message(
    interaction: discord.Interaction,
    user: discord.Member,
    message: str
):
    try:
        await interaction.response.defer(ephemeral=True)

        try:
            # Kiểm tra và thêm role cho user
            role_added = await check_and_add_role(user, CUSTOMER_ROLE_ID)
            if not role_added:
                await interaction.followup.send(
                    "❌ Không thể thêm role cho user. Vui lòng kiểm tra lại quyền của bot.",
                    ephemeral=True
                )
                return

            dm_channel = await user.create_dm()

            # Tách chuỗi thành các cặp dựa trên khoảng trắng
            pairs = message.split()
            formatted_lines = []

            # Xử lý từng cặp 3 phần tử (tk - mk)
            for i in range(0, len(pairs), 3):
                if i + 2 < len(pairs):  # Đảm bảo đủ 3 phần tử cho mỗi dòng
                    acc = pairs[i]
                    dash = pairs[i+1]  # Dấu -
                    pwd = pairs[i+2]
                    formatted_lines.append(f"{acc} {dash} {pwd}")

            # Join các dòng thành text
            accounts_text = '\n'.join(formatted_lines)

            # Tạo embed để gửi cho user
            user_embed = discord.Embed(
                title="🔑 Thông tin tài khoản",
                description=f"Format: `username - password`\nSố lượng: `{len(formatted_lines)} key`\n\n" +
                f"```\n{accounts_text}\n```" if formatted_lines else "",
                color=discord.Color.blue()
            )
            user_embed.set_footer(
                text="Lưu ý: Mỗi dòng là một tài khoản và mật khẩu")

            # Gửi embed cho user
            await dm_channel.send(embed=user_embed)

            # Tạo embed để ghi log
            log_embed = discord.Embed(
                title="📝 Log Gửi Key",
                description="Chi tiết giao dịch:",
                color=discord.Color.green(),
                timestamp=interaction.created_at
            )
            log_embed.add_field(
                name="Người gửi",
                value=f"{interaction.user.mention} (`{interaction.user.name}`)",
                inline=True
            )
            log_embed.add_field(
                name="Người nhận",
                value=f"{user.mention} (`{user.name}`)",
                inline=True
            )
            log_embed.add_field(
                name="Số lượng key",
                value=f"`{len(formatted_lines)} key`",
                inline=True
            )
            log_embed.add_field(
                name="Danh sách key",
                value=f"```\n{accounts_text}\n```",
                inline=False
            )

            # Gửi log vào channel
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=log_embed)
            else:
                print(f"Không tìm thấy channel log với ID {LOG_CHANNEL_ID}")

            await interaction.followup.send(
                f"✅ Đã gửi tin nhắn đến {user.name} và thêm role!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                f"❌ Không thể gửi tin nhắn đến {user.name}. Người dùng có thể đã chặn DM.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error sending DM: {e}")
            await interaction.followup.send(
                "❌ Có lỗi xảy ra khi gửi tin nhắn.",
                ephemeral=True
            )

    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send(
            "❌ Có lỗi xảy ra. Vui lòng thử lại sau.",
            ephemeral=True
        )


@bot.event
async def on_ready():
    print(f'🤖 {bot.user} đã sẵn sàng!')

# Thêm hàm kiểm tra và thêm role


async def check_and_add_role(member: discord.Member, role_id: int):
    """
    Kiểm tra và thêm role cho member nếu chưa có
    """
    try:
        # Lấy role từ ID
        role = member.guild.get_role(role_id)
        if not role:
            print(f"Không tìm thấy role với ID {role_id}")
            return False

        # Kiểm tra xem member đã có role chưa
        if role not in member.roles:
            await member.add_roles(role)
            print(f"Đã thêm role {role.name} cho {member.name}")
            return True
        return True
    except Exception as e:
        print(f"Lỗi khi thêm role: {e}")
        return False


@bot.tree.command(name="check", description="Kiểm tra thời hạn của key")
@app_commands.describe(
    key="Key cần kiểm tra thời hạn (nhiều key cách nhau bằng khoảng trắng)"
)
async def check_key(
    interaction: discord.Interaction,
    key: str
):
    try:
        # Defer the response since we'll make an HTTP request
        await interaction.response.defer(ephemeral=True)
        
        # Tách các key nếu có nhiều key
        key_list = [k.strip() for k in key.split() if k.strip()]
        
        if len(key_list) > 30:
            await interaction.followup.send("❌ Vui lòng kiểm tra tối đa 30 key một lần.", ephemeral=True)
            return
            
        if len(key_list) > 1:
            # Nếu có nhiều key, xử lý giống như lệnh checklist
            # Khởi tạo lists để lưu kết quả
            active_keys = []
            inactive_keys = []
            not_activated_keys = []
            error_keys = []

            # Kiểm tra từng key
            for key in key_list:
                try:
                    # Thêm delay 0.5 giây giữa các request
                    await asyncio.sleep(0.5)
                    
                    api_url = f"http://sv.hackrules.com/Robo/api.php?TK={key}"
                    for attempt in range(3):  # Thử tối đa 3 lần cho mỗi key
                        try:
                            response = requests.get(api_url, timeout=10)  # Thêm timeout
                            break
                        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                            if attempt == 2:  # Nếu đã thử 3 lần vẫn lỗi
                                error_keys.append(key)
                                continue
                            await asyncio.sleep(1)  # Chờ 1 giây trước khi thử lại
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                        except:
                            error_keys.append(key)
                            continue
                        
                        if not isinstance(data, dict):
                            error_keys.append(key)
                            continue

                        error = data.get("error")
                        message = data.get("message")
                        seconds_remaining = data.get("data")

                        if error is None or message is None:
                            error_keys.append(key)
                            continue

                        # Convert error to int if needed
                        if isinstance(error, str):
                            try:
                                error = int(error)
                            except ValueError:
                                error_keys.append(key)
                                continue

                        # Phân loại key
                        if error == 2:
                            not_activated_keys.append(key)
                        elif error != 0 or message.lower() != "ok":
                            inactive_keys.append(key)
                        else:
                            try:
                                seconds_remaining = int(seconds_remaining)
                                if seconds_remaining > 0:
                                    days_remaining = seconds_remaining // (24 * 3600)
                                    active_keys.append((key, days_remaining))
                                else:
                                    inactive_keys.append(key)
                            except (ValueError, TypeError):
                                error_keys.append(key)
                    else:
                        error_keys.append(key)

                except Exception as e:
                    print(f"Error checking key {key}: {e}")
                    error_keys.append(key)
                    continue

            # Tạo embed để hiển thị kết quả
            embed = discord.Embed(
                title="📊 Kết quả kiểm tra keys",
                color=discord.Color.blue()
            )

            # Thêm tổng kết lên đầu
            total = len(key_list)
            summary = f"Tổng số key: **{total}**\n"
            summary += f"✅ Còn hạn: **{len(active_keys)}**\n"
            summary += f"❌ Hết hạn: **{len(inactive_keys)}**\n"
            summary += f"⚠️ Chưa kích hoạt: **{len(not_activated_keys)}**\n"
            summary += f"⛔ Lỗi: **{len(error_keys)}**"
            
            embed.description = summary

            # Thêm thông tin cho từng loại key
            if active_keys:
                # Sắp xếp theo số ngày còn lại
                active_keys.sort(key=lambda x: x[1], reverse=True)
                active_keys_text = "\n".join([f"`{key}` - **{days}** ngày" for key, days in active_keys])
                if len(active_keys_text) > 1024:
                    chunks = [active_keys_text[i:i+1024] for i in range(0, len(active_keys_text), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"✅ Keys còn hạn ({len(active_keys)}) - Phần {i+1}",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name=f"✅ Keys còn hạn ({len(active_keys)})",
                        value=active_keys_text,
                        inline=False
                    )

            if inactive_keys:
                inactive_keys_text = "\n".join([f"`{key}`" for key in inactive_keys])
                if len(inactive_keys_text) > 1024:
                    chunks = [inactive_keys_text[i:i+1024] for i in range(0, len(inactive_keys_text), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"❌ Keys hết hạn ({len(inactive_keys)}) - Phần {i+1}",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name=f"❌ Keys hết hạn ({len(inactive_keys)})",
                        value=inactive_keys_text,
                        inline=False
                    )

            if not_activated_keys:
                not_activated_keys_text = "\n".join([f"`{key}`" for key in not_activated_keys])
                if len(not_activated_keys_text) > 1024:
                    chunks = [not_activated_keys_text[i:i+1024] for i in range(0, len(not_activated_keys_text), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"⚠️ Keys chưa kích hoạt ({len(not_activated_keys)}) - Phần {i+1}",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name=f"⚠️ Keys chưa kích hoạt ({len(not_activated_keys)})",
                        value=not_activated_keys_text,
                        inline=False
                    )

            if error_keys:
                error_keys_text = "\n".join([f"`{key}`" for key in error_keys])
                if len(error_keys_text) > 1024:
                    chunks = [error_keys_text[i:i+1024] for i in range(0, len(error_keys_text), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"⛔ Keys lỗi ({len(error_keys)}) - Phần {i+1}",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name=f"⛔ Keys lỗi ({len(error_keys)})",
                        value=error_keys_text,
                        inline=False
                    )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Xử lý một key duy nhất
        key = key_list[0]
        api_url = f"http://sv.hackrules.com/Robo/api.php?TK={key}"
        
        # Thử tối đa 3 lần cho single key
        for attempt in range(3):
            try:
                response = requests.get(api_url, timeout=10)
                break
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt == 2:
                    await interaction.followup.send("❌ Không thể kết nối đến server sau nhiều lần thử. Vui lòng thử lại sau.", ephemeral=True)
                    return
                await asyncio.sleep(1)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Kiểm tra xem response có đúng format không
                if not isinstance(data, dict):
                    await interaction.followup.send("❌ Định dạng dữ liệu không hợp lệ.", ephemeral=True)
                    return

                error = data.get("error")
                message = data.get("message")
                seconds_remaining = data.get("data")

                # Key không tồn tại hoặc hết hạn
                if error is None or message is None:
                    await interaction.followup.send("❌ Phản hồi từ server không đầy đủ thông tin.", ephemeral=True)
                    return

                # Convert error to int if it's string
                if isinstance(error, str):
                    try:
                        error = int(error)
                    except ValueError:
                        await interaction.followup.send("❌ Định dạng dữ liệu không hợp lệ.", ephemeral=True)
                        return

                # Kiểm tra các trường hợp error
                if error == 2:
                    await interaction.followup.send(f"⚠️ Key `{key}` chưa được kích hoạt.", ephemeral=True)
                    return
                elif error != 0 or message.lower() != "ok":
                    await interaction.followup.send("❌ Key không tồn tại hoặc đã hết hạn.", ephemeral=True)
                    return

                # Kiểm tra data cho key hợp lệ
                if seconds_remaining is None:
                    await interaction.followup.send("❌ Không lấy được thông tin thời hạn.", ephemeral=True)
                    return

                # Convert seconds_remaining to int
                try:
                    seconds_remaining = int(seconds_remaining)
                except (ValueError, TypeError):
                    await interaction.followup.send("❌ Định dạng thời gian không hợp lệ.", ephemeral=True)
                    return

                # Tính số ngày còn lại
                days_remaining = seconds_remaining // (24 * 3600)  # Chuyển giây thành ngày

                # Tạo thông báo
                if seconds_remaining > 0:
                    await interaction.followup.send(f"✅ Key `{key}` còn **{days_remaining}** ngày.", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Key `{key}` đã hết hạn.", ephemeral=True)

            except ValueError as ve:
                await interaction.followup.send("❌ Dữ liệu không hợp lệ từ server.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Không thể kết nối đến server. Vui lòng thử lại sau.", ephemeral=True)
            
    except Exception as e:
        print(f"Error checking key: {e}")
        await interaction.followup.send("❌ Có lỗi xảy ra khi kiểm tra key.", ephemeral=True)

# Run the bot
bot.run(DISCORD_TOKEN)
