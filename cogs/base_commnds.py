import disnake
from disnake.ext import commands
from disnake import Embed, SelectOption, TextInputStyle, ChannelType, ButtonStyle
from disnake.ui import View, RoleSelect, UserSelect, ChannelSelect, TextInput, Button

import requests

import json
import time
import base64
import os
from dotenv import load_dotenv, find_dotenv

from io import BytesIO
from random import randint as r
from random import choice as ch

from config import *
from audit import audit

load_dotenv(find_dotenv())

class TextImageAPI:

    def __init__(self, url):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {os.getenv('API_KEY')}',
            'X-Secret': f'Secret {os.getenv('API_SECRET')}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt: str, model, style: str, negative_prompt: str, width: int, height: int):
        params = {
            "type": "GENERATE",
            "negativePromptUnclip": negative_prompt,
            "style": style,
            "numImages": 1,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

class Base_Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        audit.info('Модуль {} активирован'.format(self.__class__.__name__))
        print(f"Модуль {self.__class__.__name__} активирован")
    
    @commands.slash_command(description="generation-style")
    @commands.has_permissions(administrator=True)
    async def styles(self, inter: disnake.ApplicationCommandInteraction):
       
        response = requests.get("https://cdn.fusionbrain.ai/static/styles/api")
        if response.status_code != 200:
            return await inter.send("Failed to retrieve styles. Please try again later.")
        
        styles = response.json()
        embeds_list = []
        
        for style in styles:
            name = style["name"]
            title_en = style["titleEn"]
            image_url = style["image"]

            embed = disnake.Embed(
                title=name,
                description=title_en,
                color=0x2b2d31
            )
            
            embed.set_image(url=image_url)
            embeds_list.append(embed)
            
        await inter.send(embeds=embeds_list)
    
    @commands.slash_command(description="generation-by-model")
    @commands.has_permissions(administrator=True)
    async def generation(self,
                        inter: disnake.ApplicationCommandInteraction,
                        prompt: str = commands.Param(
                            name = 'request',
                            description = 'Image request text and emoji.'
                        ),
                        negative_prompt: str = commands.Param(
                            name = 'negative-prompt',
                            description = 'What colors and techniques the model should not use when generating an image.',
                            default = None
                        ),
                        quantity: commands.Range[int, 1, 4] = commands.Param(
                            name = "quantity",
                            description = "Quantity for image.",
                            default = 1
                        ),
                        style: str = commands.Param(
                            name = 'style',
                            description = 'Generated image stylе.',
                            choices=["ANIME", "DEFAULT", "UHD", "KANDINSKY"],
                            default="DEFAULT"
                        ),
                        width: commands.Range[int, 100, 1024] = commands.Param(
                            name = "width",
                            description = "Width for image.",
                            default = 1024
                        ),
                        height: commands.Range[int, 100, 1024] = commands.Param(
                            name = "height",
                            description = "Height for image.",
                            default = 1024
                        ),
                        ):
        
        await inter.response.defer(with_message=True)
        
        api = TextImageAPI('https://api-key.fusionbrain.ai/')
        model_id = api.get_model()
        
        files = []
        progress_message = await inter.edit_original_message("Generating images...")
        for i in range(quantity):
            uuid = api.generate(prompt, model_id, style, negative_prompt, width, height)
            images = api.check_generation(uuid)
            image_base64 = images[0]
            image_data = base64.b64decode(image_base64)
            file = disnake.File(fp=BytesIO(image_data), filename=f"{prompt.split('.')[0]} _ {r(0, 100000)}.jpg")
            files.append(file)
            await progress_message.edit(content=f"Generated `{i+1}/{quantity}` images...")

        await progress_message.edit(content=f"Generated images for `{prompt}`:", files=files)
    
def setup(bot: commands.Bot):
    bot.add_cog(Base_Commands(bot))