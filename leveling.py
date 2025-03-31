
class LevelSystem:
    def __init__(self):
        self.user_xp = {}
        self.xp_per_message = 5
        
    def add_xp(self, user_id: str, amount: int = None):
        if amount is None:
            amount = self.xp_per_message
            
        if user_id not in self.user_xp:
            self.user_xp[user_id] = {"xp": 0, "level": 1}
            
        self.user_xp[user_id]["xp"] += amount
        return self.check_level_up(user_id)
    
    def check_level_up(self, user_id: str):
        user = self.user_xp[user_id]
        current_level = user["level"]
        xp_needed = current_level * 100
        
        if user["xp"] >= xp_needed:
            user["level"] += 1
            user["xp"] -= xp_needed
            return user["level"]
        return None
        
    def get_level_info(self, user_id: str):
        if user_id not in self.user_xp:
            self.user_xp[user_id] = {"xp": 0, "level": 1}
        return self.user_xp[user_id]
