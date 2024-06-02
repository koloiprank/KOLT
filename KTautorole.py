import discord
import KTtools


#Automatic on-join
async def automatic_onjoin(interaction : discord.Interaction) -> None:
    embed = discord.Embed(
        title = "On-join autorole config",
        description="Select which roles you want to assign to new members on-join from the dropdown below.",
        colour = discord.Colour.dark_purple()
    )
    
    await interaction.response.send_message(embed = embed, view = RolesView(interaction.guild))

class RolesDropdown(discord.ui.Select):
    
    def __init__(self, guild : discord.Guild) -> None:
        
        roles = list(guild.roles)
        options = [ discord.SelectOption( label = role.name, value = role.id) for role in roles ]
        
        super().__init__(placeholder = "Select roles", options=options, min_values=1, max_values = len(roles))  

    async def callback(self, interaction : discord.Interaction) -> None:
        selected_roles = self.values
        config = await KTtools.load_config(str(interaction.guild.id))
        config["onjoin_roles"] = list(selected_roles)
        await KTtools.save_config(config, str(interaction.guild.id))
        
        embed = discord.Embed(
            description= "Roles selected: " + ", ".join(interaction.user.guild.get_role(int(role)).name for role in selected_roles),
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed = embed)
class RolesView(discord.ui.View):
    
    def __init__(self, guild : discord.Guild) -> None:
        super().__init__()
        self.add_item(RolesDropdown(guild))
