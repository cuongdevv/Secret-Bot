import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from urllib.parse import quote
import requests
from datetime import datetime
import asyncio
import aiohttp  # Thêm import aiohttp cho async requests

# Load environment variables
load_dotenv()

# Configuration from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BANK_ID = os.getenv('BANK_ID', '970436')
ACCOUNT_NO = os.getenv('ACCOUNT_NO')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME')
# Thêm API_KEY cho lệnh addtime
API_KEY = os.getenv('API_KEY')

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


async def check_single_key(session, key):
    """
    Hàm kiểm tra một key riêng lẻ
    """
    api_url = f"http://sv.hackrules.com/API/api.php?TK={key}"
    
    for attempt in range(3):  # Thử tối đa 3 lần
        try:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        
                        if not isinstance(data, dict):
                            return (key, "error")

                        error = data.get("error")
                        message = data.get("message")
                        seconds_remaining = data.get("data")

                        if error is None or message is None:
                            return (key, "error")

                        # Convert error to int if needed
                        if isinstance(error, str):
                            try:
                                error = int(error)
                            except ValueError:
                                return (key, "error")

                        # Phân loại key
                        if error == 2:
                            return (key, "not_activated")
                        elif error != 0 or message.lower() != "ok":
                            return (key, "inactive")
                        else:
                            try:
                                seconds_remaining = int(seconds_remaining)
                                if seconds_remaining > 0:
                                    days_remaining = seconds_remaining // (24 * 3600)
                                    return (key, "active", days_remaining)
                                else:
                                    return (key, "inactive")
                            except (ValueError, TypeError):
                                return (key, "error")
                    except:
                        if attempt == 2:
                            return (key, "error")
                else:
                    if attempt == 2:
                        return (key, "error")
        except:
            if attempt == 2:
                return (key, "error")
        await asyncio.sleep(1)
    return (key, "error")

@bot.tree.command(name="check", description="Kiểm tra thời hạn của key")
@app_commands.describe(
    key="Key cần kiểm tra thời hạn (nhiều key cách nhau bằng khoảng trắng)"
)
async def check_key(
    interaction: discord.Interaction,
    key: str
):
    try:
        # Defer the response since we'll make HTTP requests
        await interaction.response.defer(ephemeral=True)
        
        # Tách các key nếu có nhiều key
        key_list = [k.strip() for k in key.split() if k.strip()]
        
        if len(key_list) > 30:
            await interaction.followup.send("❌ Vui lòng kiểm tra tối đa 30 key một lần.", ephemeral=True)
            return
            
        if len(key_list) > 1:
            # Khởi tạo lists để lưu kết quả
            active_keys = []
            inactive_keys = []
            not_activated_keys = []
            error_keys = []

            # Tạo session để tái sử dụng connection
            async with aiohttp.ClientSession() as session:
                # Chạy tất cả requests đồng thời
                tasks = [check_single_key(session, key) for key in key_list]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Phân loại kết quả
                for result in results:
                    if isinstance(result, tuple):
                        key = result[0]
                        status = result[1]
                        if status == "active":
                            active_keys.append((key, result[2]))  # result[2] là số ngày
                        elif status == "inactive":
                            inactive_keys.append(key)
                        elif status == "not_activated":
                            not_activated_keys.append(key)
                        else:
                            error_keys.append(key)
                    else:
                        error_keys.append(key)

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
        async with aiohttp.ClientSession() as session:
            result = await check_single_key(session, key_list[0])
            
            if result[1] == "active":
                await interaction.followup.send(f"✅ Key `{result[0]}` còn **{result[2]}** ngày.", ephemeral=True)
            elif result[1] == "not_activated":
                await interaction.followup.send(f"⚠️ Key `{result[0]}` chưa được kích hoạt.", ephemeral=True)
            elif result[1] == "inactive":
                await interaction.followup.send(f"❌ Key `{result[0]}` đã hết hạn hoặc không tồn tại.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Có lỗi xảy ra khi kiểm tra key.", ephemeral=True)

    except Exception as e:
        print(f"Error checking key: {e}")
        await interaction.followup.send("❌ Có lỗi xảy ra khi kiểm tra key.", ephemeral=True)


@bot.tree.command(name="addtime", description="Thêm thời gian cho key")
@app_commands.describe(
    account="Tài khoản cần thêm thời gian (nhiều tài khoản cách nhau bằng khoảng trắng)",
    hours="Số giờ cần thêm"
)
async def add_time(
    interaction: discord.Interaction,
    account: str,
    hours: int
):
    try:
        # Kiểm tra quyền admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
            return
            
        # Kiểm tra số giờ
        if hours <= 0:
            await interaction.response.send_message("❌ Số giờ phải lớn hơn 0!", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        # Tách các tài khoản nếu có nhiều tài khoản
        account_list = [acc.strip() for acc in account.split() if acc.strip()]
        
        if len(account_list) > 30:
            await interaction.followup.send("❌ Vui lòng thêm thời gian tối đa 30 tài khoản một lần.", ephemeral=True)
            return
        
        # Khởi tạo lists để lưu kết quả
        success_accounts = []
        failed_accounts = []
        
        # Tạo session để tái sử dụng connection
        async with aiohttp.ClientSession() as session:
            # Hàm xử lý thêm thời gian cho một tài khoản
            async def add_time_single(session, account):
                api_url = f"http://sv.hackrules.com/API/addtime.php?API={API_KEY}&TK={account}&SOGIO={hours}"
                try:
                    async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.text()
                            try:
                                # Thử parse JSON từ phản hồi
                                json_data = await response.json()
                                # Kiểm tra nếu message là "OK" thì coi là thành công
                                if json_data.get("message") == "OK":
                                    return (account, True, "Thành công")
                                else:
                                    return (account, False, f"Lỗi: {data}")
                            except:
                                # Nếu không phải JSON, kiểm tra theo cách cũ
                                if "success" in data.lower() or "ok" in data.lower():
                                    return (account, True, "Thành công")
                                else:
                                    return (account, False, f"Lỗi: {data}")
                        else:
                            return (account, False, f"Mã lỗi: {response.status}")
                except Exception as e:
                    return (account, False, str(e))
            
            # Chạy tất cả requests đồng thời
            tasks = [add_time_single(session, acc) for acc in account_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Phân loại kết quả
            for result in results:
                if isinstance(result, tuple):
                    acc = result[0]
                    success = result[1]
                    message = result[2]
                    if success:
                        success_accounts.append(acc)
                    else:
                        failed_accounts.append((acc, message))
                else:
                    # Xử lý trường hợp exception
                    failed_accounts.append((account_list[results.index(result)], "Lỗi không xác định"))
        
        # Tạo embed để hiển thị kết quả
        embed = discord.Embed(
            title="📊 Kết quả thêm thời gian",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        
        # Thêm tổng kết lên đầu
        total = len(account_list)
        summary = f"Tổng số tài khoản: **{total}**\n"
        summary += f"✅ Thành công: **{len(success_accounts)}**\n"
        summary += f"❌ Thất bại: **{len(failed_accounts)}**\n"
        summary += f"⏱️ Số giờ đã thêm: **{hours}** giờ/tài khoản"
        
        embed.description = summary
        
        # Thêm thông tin cho từng loại tài khoản
        if success_accounts:
            success_accounts_text = "\n".join([f"`{acc}`" for acc in success_accounts])
            if len(success_accounts_text) > 1024:
                chunks = [success_accounts_text[i:i+1024] for i in range(0, len(success_accounts_text), 1024)]
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"✅ Tài khoản thành công ({len(success_accounts)}) - Phần {i+1}",
                        value=chunk,
                        inline=False
                    )
            else:
                embed.add_field(
                    name=f"✅ Tài khoản thành công ({len(success_accounts)})",
                    value=success_accounts_text,
                    inline=False
                )
        
        if failed_accounts:
            failed_accounts_text = "\n".join([f"`{acc}` - {msg}" for acc, msg in failed_accounts])
            if len(failed_accounts_text) > 1024:
                chunks = [failed_accounts_text[i:i+1024] for i in range(0, len(failed_accounts_text), 1024)]
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"❌ Tài khoản thất bại ({len(failed_accounts)}) - Phần {i+1}",
                        value=chunk,
                        inline=False
                    )
            else:
                embed.add_field(
                    name=f"❌ Tài khoản thất bại ({len(failed_accounts)})",
                    value=failed_accounts_text,
                    inline=False
                )
        
        # Gửi kết quả cho người dùng
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Gửi log vào channel
        if success_accounts:
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📝 Log Thêm Thời Gian",
                    description="Chi tiết thao tác:",
                    color=discord.Color.blue(),
                    timestamp=interaction.created_at
                )
                log_embed.add_field(
                    name="Người thực hiện",
                    value=f"{interaction.user.mention} (`{interaction.user.name}`)",
                    inline=True
                )
                log_embed.add_field(
                    name="Số tài khoản",
                    value=f"`{len(success_accounts)}/{total}`",
                    inline=True
                )
                log_embed.add_field(
                    name="Số giờ thêm",
                    value=f"`{hours} giờ`",
                    inline=True
                )
                
                # Thêm danh sách tài khoản thành công
                success_accounts_text = "\n".join([f"`{acc}`" for acc in success_accounts])
                if len(success_accounts_text) > 1024:
                    chunks = [success_accounts_text[i:i+1024] for i in range(0, len(success_accounts_text), 1024)]
                    for i, chunk in enumerate(chunks):
                        log_embed.add_field(
                            name=f"Tài khoản đã thêm thời gian - Phần {i+1}",
                            value=chunk,
                            inline=False
                        )
                else:
                    log_embed.add_field(
                        name="Tài khoản đã thêm thời gian",
                        value=success_accounts_text,
                        inline=False
                    )
                
                await log_channel.send(embed=log_embed)
                
    except Exception as e:
        print(f"Error in addtime command: {e}")
        await interaction.followup.send("❌ Có lỗi xảy ra. Vui lòng thử lại sau.", ephemeral=True)

# Run the bot
bot.run(DISCORD_TOKEN)
