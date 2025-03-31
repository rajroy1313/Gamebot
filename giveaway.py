import random
import time
from typing import Dict, List, Optional

class Giveaway:
    def __init__(self):
        self.active_giveaways: Dict[str, dict] = {}
        self.giveaway_history: List[dict] = []

    def create_giveaway(self, channel_id: str, prize: str, duration: int, host_id: str) -> str:
        giveaway_id = str(int(time.time()))
        self.active_giveaways[giveaway_id] = {
            'prize': prize,
            'end_time': time.time() + (duration * 60),
            'participants': [],
            'channel_id': channel_id,
            'host_id': host_id,
            'winner': None
        }
        return giveaway_id

    def join_giveaway(self, giveaway_id: str, user_id: str) -> bool:
        if giveaway_id in self.active_giveaways:
            if user_id not in self.active_giveaways[giveaway_id]['participants']:
                self.active_giveaways[giveaway_id]['participants'].append(user_id)
                return True
        return False

    def end_giveaway(self, giveaway_id: str) -> Optional[dict]:
        if giveaway_id in self.active_giveaways:
            giveaway = self.active_giveaways[giveaway_id]
            if giveaway['participants']:
                winner = random.choice(giveaway['participants'])
                giveaway['winner'] = winner
                participant_count = len(giveaway['participants'])
                del self.active_giveaways[giveaway_id]
                return {'prize': giveaway['prize'], 'winner': winner, 'participant_count': participant_count}
        return None

    def get_giveaway(self, giveaway_id: str) -> Optional[dict]:
        return self.active_giveaways.get(giveaway_id)

    def reroll_winner(self, giveaway_id: str) -> Optional[dict]:
        if giveaway_id in self.active_giveaways:
            giveaway = self.active_giveaways[giveaway_id]
            if giveaway['participants']:
                old_winner = giveaway.get('winner')
                while True:
                    new_winner = random.choice(giveaway['participants'])
                    if new_winner != old_winner or len(giveaway['participants']) == 1:
                        giveaway['winner'] = new_winner
                        return {'prize': giveaway['prize'], 'winner': new_winner}
        return None

    def get_participants(self, giveaway_id: str) -> Optional[List[str]]:
        if giveaway_id in self.active_giveaways:
            return self.active_giveaways[giveaway_id]['participants']
        return None

    def add_to_history(self, giveaway_data: dict):
        self.giveaway_history.append({
            'prize': giveaway_data['prize'],
            'winner': giveaway_data['winner'],
            'participants': giveaway_data['participants'],
            'end_time': giveaway_data['end_time']
        })

    def get_history(self, limit: int = 5) -> List[dict]:
        return self.giveaway_history[-limit:]