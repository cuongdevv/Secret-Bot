import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from urllib.parse import quote
import requests
from datetime import datetime

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
    key="Key cần kiểm tra thời hạn"
)
async def check_key(
    interaction: discord.Interaction,
    key: str
):
    try:
        # Defer the response since we'll make an HTTP request
        await interaction.response.defer(ephemeral=True)
        
        # Make the API request
        api_url = f"http://sv.hackrules.com/Robo/api.php?TK={key}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API Response for key {key}: {data}")  # Debug log
                
                # Kiểm tra xem response có đúng format không
                if not isinstance(data, dict):
                    await interaction.followup.send("❌ Định dạng dữ liệu không hợp lệ.", ephemeral=True)
                    return

                error = data.get("error")
                message = data.get("message")
                timestamp = data.get("data")

                print(f"Parsed data - error: {error}, message: {message}, timestamp: {timestamp}")  # Debug log

                # Key không tồn tại hoặc hết hạn
                if error is None or message is None or timestamp is None:
                    await interaction.followup.send("❌ Phản hồi từ server không đầy đủ thông tin.", ephemeral=True)
                    return
                    
                if isinstance(timestamp, str):
                    try:
                        timestamp = int(timestamp)
                    except ValueError:
                        await interaction.followup.send("❌ Định dạng thời gian không hợp lệ.", ephemeral=True)
                        return

                # Convert timestamp to datetime
                expiry_date = datetime.fromtimestamp(timestamp)
                current_time = datetime.now()
                
                # Tính thời gian còn lại
                time_left = expiry_date - current_time
                days_left = time_left.days
                
                # Create embed for response
                embed = discord.Embed(
                    title="🔍 Thông tin key",
                    color=discord.Color.green() if days_left > 0 else discord.Color.red()
                )
                
                embed.add_field(
                    name="Key",
                    value=f"`{key}`",
                    inline=False
                )
                
                embed.add_field(
                    name="Thời hạn",
                    value=f"<t:{timestamp}:F>",
                    inline=False
                )

                embed.add_field(
                    name="Trạng thái",
                    value=f"{'🟢 Còn ' + str(days_left) + ' ngày' if days_left > 0 else '🔴 Đã hết hạn'}",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            except ValueError as ve:
                print(f"ValueError while processing response: {ve}")  # Debug log
                await interaction.followup.send("❌ Dữ liệu không hợp lệ từ server.", ephemeral=True)
        else:
            print(f"HTTP Error: Status code {response.status_code}")  # Debug log
            await interaction.followup.send("❌ Không thể kết nối đến server. Vui lòng thử lại sau.", ephemeral=True)
            
    except Exception as e:
        print(f"Error checking key: {e}")
        await interaction.followup.send("❌ Có lỗi xảy ra khi kiểm tra key.", ephemeral=True)

# Run the bot
bot.run(DISCORD_TOKEN)
