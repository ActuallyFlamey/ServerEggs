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