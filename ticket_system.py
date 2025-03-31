
class TicketSystem:
    def __init__(self):
        self.tickets = {}
        self.ticket_counter = 0
        self.support_role_ids = []
        self.admin_role_ids = []
        
    def set_roles(self, support_roles: list, admin_roles: list):
        self.support_role_ids = support_roles
        self.admin_role_ids = admin_roles
        
    def has_permission(self, user_roles: list, required_roles: list) -> bool:
        return any(str(role) in required_roles for role in user_roles)
        
    def create_ticket(self, user_id: str, channel_id: str, issue: str):
        self.ticket_counter += 1
        ticket_id = f"TICKET-{self.ticket_counter}"
        
        self.tickets[ticket_id] = {
            "user_id": user_id,
            "channel_id": channel_id,
            "issue": issue,
            "status": "open",
            "responses": []
        }
        return ticket_id
        
    def close_ticket(self, ticket_id: str):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = "closed"
            return True
        return False
        
    def add_response(self, ticket_id: str, user_id: str, response: str):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["responses"].append({
                "user_id": user_id,
                "response": response
            })
            return True
        return False
        
    def get_ticket(self, ticket_id: str):
        return self.tickets.get(ticket_id)
        
    def get_user_tickets(self, user_id: str):
        return {tid: ticket for tid, ticket in self.tickets.items() 
                if ticket["user_id"] == user_id}
