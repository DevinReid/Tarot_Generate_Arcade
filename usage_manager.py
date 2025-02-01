# usage_manager.py
  ##WIP
class UsageManager:
    def __init__(self, max_cost=30.0):
        """
        max_cost: float - The maximum total cost in USD you want to allow
        """
        self.max_cost = max_cost
        self.total_cost = 0.0  # total cost so far

    def can_afford_request(self, estimated_cost):
        """
        Return True if there's enough "budget" left to afford the next request.
        """
        return (self.total_cost + estimated_cost) <= self.max_cost

    def add_cost(self, cost):
        """
        Increments the total cost by 'cost'
        """
        self.total_cost += cost
        # Optionally, persist self.total_cost to disk or a database.

    def get_remaining_budget(self):
        return self.max_cost - self.total_cost


def estimate_cost(num_prompt_tokens, num_completion_tokens=100):
    """
    Roughly estimate the cost based on token usage rates.
    """
    # Example: GPT-4o-mini rates
    input_rate = 0.15 / 1_000_000
    cached_input_rate = 0.075 / 1_000_000
    output_rate = 0.6 / 1_000_000

    # For a rough guess, assume all tokens are 'input' tokens (not cached)
    input_cost = num_prompt_tokens * input_rate
    completion_cost = num_completion_tokens * output_rate

    return input_cost + completion_cost


def record_actual_usage(resp, usage_manager):
    input_rate = 0.15 / 1_000_000
    cached_input_rate = 0.075 / 1_000_000
    output_rate = 0.6 / 1_000_000

    cached_input_cost = resp.usage.prompt_tokens_details.cached_tokens * cached_input_rate
    input_cost = (resp.usage.prompt_tokens - resp.usage.prompt_tokens_details.cached_tokens) * input_rate
    output_cost = resp.usage.completion_tokens * output_rate
    total_cost = cached_input_cost + input_cost + output_cost
    
    usage_manager.add_cost(total_cost)
    
    print("\nDEBUG: Actual Usage")
    print(f"Prompt tokens: {resp.usage.prompt_tokens}")
    print(f"Cached Prompt tokens: {resp.usage.prompt_tokens_details.cached_tokens}")
    print(f"Completion tokens: {resp.usage.completion_tokens}")
    print(f"Total tokens: {resp.usage.total_tokens}")
    print("\nDEBUG: Actual Cost")
    print(f"Prompt tokens: {input_cost}")
    print(f"Cached Prompt tokens: {cached_input_cost}")
    print(f"Completion tokens: {output_cost}")
    print(f"Total cost: {total_cost}")
    print(f"Remaining budget: ${usage_manager.get_remaining_budget():.2f}")
