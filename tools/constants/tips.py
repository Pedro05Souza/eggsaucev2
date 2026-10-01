from .bot_constants import MAX_GENERATED_CHICKENS, STEAL_FAILURE_CHANCE

__all__ = ["TIPS"]

TIPS = [
    "The currency name is eggbux.",
    "You can buy titles with eggbux that generate passive income forever.",
    "Unhappy chickens lay fewer eggs and can devolve. Feed them with feedall.",
    "You can trade chickens with other players.",
    "New here? The guide command explains the game and pays you for your first steps.",
    "You can evolve two chickens of the same rarity into the next rarity, except for ascended chickens.",
    "You can inspect all the interesting attributes of a chicken with inspectchicken command.",
    "The quality attribute of a chicken determines its maximum egg production.",
    "Buying farmers will give you permanent bonuses.",
    "Extra corn can be sold for eggbux with the sellcorn command.",
    "Your cornfield grows corn every hour, even while you're away.",
    f"The market command generates {MAX_GENERATED_CHICKENS} chickens.",
    "The battle command allows you to battle your chickens against other players' chickens.",
    "Ethereal chickens always have 100% quality.",
    "Use the vault command to protect your best chickens from battles and devolving.",
    "Friendly battles let you compete without losing rank or MMR.",
    "Eggbux in the bank can't be stolen. Deposit them with deposit all.",
    "Your bank has a limit; upgrade it with upgradebank to store more wealth safely.",
    "Gifting and trading chickens are great ways to help other players get started.",
    "Redeemables contain special chickens you earned from events and rank-ups.",
    "You can rename your farm and individual chickens to give them personality.",
    "Use the farmprofit command to plan your income strategy.",
    f"Stealing fails {int(STEAL_FAILURE_CHANCE * 100)}% of the time, so invest in your title for steady income.",
    "Trading 8 ascended chickens for 1 ethereal is the ultimate endgame goal.",
    "Buying plots for your cornfield is one of the best early-game investments.",
]
