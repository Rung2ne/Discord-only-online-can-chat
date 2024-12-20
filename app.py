import discord
from discord.ext import commands
import os
import json

# TOKEN 설정
TOKEN = f'당신의 토큰'

# 봇 로딩
class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        try:
            synced = await self.tree.sync()
            print(f'{len(synced)}개의 명령어가 서버에 동기화되었습니다.')

        except Exception as e:
            print(f'Error syncing commands: {e}')

intents = discord.Intents.all()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

# 메시지 제한 로그를 남길 채널 ID
log_channel_id = 1234567890 

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return  # 봇이 보낸 메시지는 무시

    # 유저 상태 확인 (오프라인, 자리비움, 방해금지 순)
    user_status = message.author.status
    if user_status in [discord.Status.offline, discord.Status.idle, discord.Status.dnd]:
        try:
            # 위의 3개 상태라면 메시지 삭제
            await message.delete()

            # 유저에게 지금 상태가 온라인이 아니라고 임베드 전송
            embed = discord.Embed(
                title="메시지가 삭제되었습니다.",
                description=(
                    "온라인 상태가 아니므로 메시지를 보낼 수 없습니다.\n"
                    "상태를 변경하고 다시 시도해 주세요."
                ),
                color=0xff0000
            )
            embed.set_footer(text="온라인 이외의 상태의 유저는 메시지 전송이 제한됩니다.")
            await message.channel.send(embed=embed, delete_after=10)  # 임베드는 10초 후 삭제

            # 로그 채널에 기록
            log_channel = client.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="메시지 삭제 로그",
                    description=f"온라인 상태가 아닌 사용자가 메시지를 보냈습니다.",
                    color=0xffa500
                )
                log_embed.add_field(name="사용자", value=f"{message.author} ({message.author.id})", inline=False)
                log_embed.add_field(name="채널", value=f"{message.channel.name} ({message.channel.id})", inline=False)
                log_embed.add_field(name="내용", value=message.content, inline=False)
                log_embed.set_footer(text="오프라인/자리비움/방해금지 상태 사용자 메시지 제한 로그")
                await log_channel.send(embed=log_embed)
        except discord.Forbidden:
            print("봇의 권한 부족으로 메시지를 삭제하거나 로그를 남길 수 없습니다.")
        except discord.HTTPException as e:
            print(f"메시지 처리 중 오류 발생: {e}")
    else:
        await client.process_commands(message)  # 명령어 처리

# 봇 실행
client.run(TOKEN)
