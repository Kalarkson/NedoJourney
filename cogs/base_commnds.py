import disnake
from disnake.ext import commands
from disnake import Embed, SelectOption, TextInputStyle, ChannelType, ButtonStyle
from disnake.ui import View, RoleSelect, UserSelect, ChannelSelect, TextInput, Button

from config import *
from audit import audit

import chat_exporter, io, datetime
from io import BytesIO

class Base_Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        audit.info('Модуль {} активирован'.format(self.__class__.__name__))
        print(f"Модуль {self.__class__.__name__} активирован")
       
    
    
def setup(bot: commands.Bot):
    bot.add_cog(Base_Commands(bot))