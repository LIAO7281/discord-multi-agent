"""
Discord Bot - 主入口
多 Agent 协作 Discord 客服系统
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from typing import Dict, Any, List

from src.agents.intent_agent import IntentAgent
from src.agents.reply_agent import ReplyAgent
from src.agents.quality_agent import QualityAgent


# 加载环境变量
load_dotenv()

# 初始化三个 Agent
intent_agent = IntentAgent()
reply_agent = ReplyAgent()
quality_agent = QualityAgent()

# Discord Bot 配置
intents = discord.Intents.default()
intents.message_content = True  # 需要勾选 Discord Developer Portal 的 "Message Content Intent"

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Bot 启动完成"""
    print(f'✅ {bot.user} 已上线！')
    print(f'📊 已加载 Agents: IntentAgent, ReplyAgent, QualityAgent')
    print(f'🔗 邀请链接: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot')


@bot.event 
async def on_message(message: discord.Message):
    """处理所有消息"""
    # 忽略自己发的消息
    if message.author == bot.user:
        return
    
    # 忽略以 ! 开头的命令
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    # 只处理有内容的消息
    if not message.content:
        return
    
    # 🚀 启动多 Agent 协作流程
    channel = message.channel
    async with channel.typing():  # 显示 "正在输入..."
        
        # Step 1: 意图识别
        intent_result = intent_agent.process({
            "message": message.content,
            "user_id": str(message.author.id),
            "channel_id": str(message.channel.id),
            "history": await _get_history(message.channel, limit=5)
        })
        
        print(f"📥 Intent: {intent_result['intent']} (conf: {intent_result['confidence']:.2f})")
        
        # 如果需要转人工，直接通知
        if intent_result.get("requires_human"):
            await channel.send("👥 已为您转接人工客服，请稍候...")
            return
        
        # Step 2: 生成回复
        reply_result = reply_agent.process({
            "message": message.content,
            "intent": intent_result,
            "user_id": str(message.author.id),
            "channel_id": str(message.channel.id),
            "history": await _get_history(message.channel, limit=5)
        })
        
        print(f"💬 Reply generated (conf: {reply_result['confidence']:.2f})")
        
        # Step 3: 质量审核
        quality_result = quality_agent.process({
            "original_message": message.content,
            "intent": intent_result,
            "reply": reply_result["reply"],
            "user_id": str(message.author.id),
            "history": await _get_history(message.channel, limit=5)
        })
        
        print(f"✅ Quality: {quality_result['action']} (score: {quality_result['score']:.2f})")
        
        # Step 4: 根据审核结果采取行动
        action = quality_result["action"]
        
        if action == "send":
            # 直接发送
            await channel.send(quality_result["final_reply"])
            
        elif action == "rewrite":
            # 发送重写版本
            await channel.send(quality_result["final_reply"])
            
        elif action == "human":
            # 转人工
            await channel.send("👥 此问题需要人工客服处理，已通知团队...")
            # 可选：在管理频道发送通知
            # admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
            # if admin_channel: await admin_channel.send(f"⚠️ 需要人工处理: {message.content}")
            
        else:
            # 默认发送
            await channel.send(quality_result["final_reply"])


async def _get_history(channel: discord.TextChannel, limit: int = 5) -> List[Dict[str, str]]:
    """获取最近的历史消息"""
    history = []
    async for msg in channel.history(limit=limit):
        role = "user" if msg.author != bot.user else "assistant"
        history.append({
            "role": role,
            "content": msg.content
        })
    return history


@bot.command()
async def ping(ctx):
    """测试 Bot 是否在线"""
    await ctx.send("🏓 Pong! 多 Agent 系统运行中...")


@bot.command()
async def agents(ctx):
    """查看已加载的 Agents"""
    embed = discord.Embed(title="🤖 已加载的 Agents", color=0x00ff00)
    embed.add_field(name="IntentAgent", value="意图识别", inline=False)
    embed.add_field(name="ReplyAgent", value="回复生成", inline=False)
    embed.add_field(name="QualityAgent", value="质量审核", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def reload(ctx):
    """重新加载 Agents（开发用）"""
    global intent_agent, reply_agent, quality_agent
    intent_agent = IntentAgent()
    reply_agent = ReplyAgent()
    quality_agent = QualityAgent()
    await ctx.send("✅ Agents 重新加载完成")


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ 未找到 DISCORD_TOKEN 环境变量！请检查 .env 文件")
        exit(1)
    
    print("🚀 正在启动 Discord Multi-Agent Support System...")
    bot.run(token)