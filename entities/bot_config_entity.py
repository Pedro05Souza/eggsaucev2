from dataclasses import dataclass

@dataclass
class BotConfigEntity():
    
    __slots__ = ["config_id", "guild_id", "toggled_modules", "prefix", "allowed_channels"]
    
    config_id: int
    guild_id: int
    toggled_modules: str
    prefix: str
    allowed_channels: list[int]