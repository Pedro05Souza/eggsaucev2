from dataclasses import dataclass

@dataclass
class BankPlayerEntity:
    
    __slots__ = ["bank_player_id", "bank_balance", "bank_upgrades"]
    
    bank_player_id: str
    bank_balance: int
    bank_upgrades: int
    