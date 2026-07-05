import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

# Botの初期設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 2. 応募内容を入力させるポップアップ画面（モーダル）
class RecruitmentModal(discord.ui.Modal):
    def __init__(self, role_name):
        # 選択された職種名をタイトルにする
        super().__init__(title=f'{role_name}への応募')
        self.role_name = role_name

        self.name = discord.ui.TextInput(
            label='お名前（またはニックネーム）',
            style=discord.TextStyle.short,
            placeholder='例: ヤマダ太郎',
            required=True
        )
        self.add_item(self.name)

        self.pr = discord.ui.TextInput(
            label='自己PR・実績など',
            style=discord.TextStyle.paragraph,
            placeholder='あなたのスキルや意気込みを教えてください！',
            required=True
        )
        self.add_item(self.pr)

    async def on_submit(self, interaction: discord.Interaction):
        # 応募完了メッセージを送信（応募した本人にしか見えません）
        await interaction.response.send_message(
            f'🎉 ありがとうございます！\n**{self.role_name}**にご応募いただきました。後ほど運営よりご連絡いたします。',
            ephemeral=True
        )
        # Renderのログに応募内容を出力（実運用ではここで指定のチャンネルに通知を送るなどの処理を書きます）
        print(f"【新規応募】職種: {self.role_name} | 名前: {self.name.value} | PR: {self.pr.value}")

# 1. 職種を選ぶプルダウンメニュー
class RecruitmentSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='デベロッパー（開発者）', description='システム開発を担当します', emoji='💻'),
            discord.SelectOption(label='運営スタッフ', description='コミュニティの運営を行います', emoji='🤝'),
            discord.SelectOption(label='管理者', description='プロジェクト全体の管理を行います', emoji='👑')
        ]
        super().__init__(placeholder='ここから希望する職種を選んでください', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # 選ばれた職種を取得し、上記のモーダル（入力画面）を呼び出す
        role_name = self.values[0]
        await interaction.response.send_modal(RecruitmentModal(role_name))

# プルダウンをメッセージに組み込むためのView
class RecruitmentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RecruitmentSelect())

# Bot起動時の処理
@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user}')

# 募集パネルを設置するコマンド（!recruit とチャットで打つとメニューが出ます）
@bot.command()
async def recruit(ctx):
    embed = discord.Embed(
        title="✨ プロジェクト・スタッフ募集 ✨",
        description="一緒にプロジェクトを盛り上げてくれる仲間を募集しています！\n下のメニューから希望する職種を選択してご応募ください。",
        color=0x00b0f4
    )
    await ctx.send(embed=embed, view=RecruitmentView())

# --- 起動処理 ---
# 1. Render対策のWebサーバーをバックグラウンドで起動
keep_alive()

# 2. Discord Botを起動
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("エラー: DISCORD_TOKENが設定されていません。")
