import os

import discord


class GetEgg(discord.ui.View):
    def __init__(self, lines: dict, creator: discord.User, origin):
        super().__init__(timeout=None)

        if origin.invite is not None:
            self.add_item(
                discord.ui.Button(
                    label=lines["button"]["origin"],
                    url=origin.invite
                )
            )
        
        if creator is not None:
            self.add_item(
                discord.ui.Button(
                    label=lines["button"]["creator"],
                    url=f"https://discord.com/users/{creator.id}"
                )
            )

class DeleteEgg(discord.ui.View):
    def __init__(self, lines: dict, egg):
        super().__init__(timeout=60)
        
        self.lines = lines
        self.egg = egg

        self.confirm.label = lines["confirm"]
    
    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.Button):
        if self.egg.attach_path and os.path.exists(self.egg.attach_path):
            try:
                os.remove(self.egg.attach_path)
            except OSError:
                print(f"log: failed to delete attachment for Egg {self.egg.id}")
        
        eggid = self.egg.id

        await self.egg.delete()

        await ctx.response.edit_message(content=self.lines["success"].format(eggid), embed=None, attachments=[], view=None)