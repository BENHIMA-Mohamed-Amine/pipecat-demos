from dataclasses import dataclass


@dataclass
class BotConfig:
    greeting: str = "Please introduce yourself to the user in one sentenc."
