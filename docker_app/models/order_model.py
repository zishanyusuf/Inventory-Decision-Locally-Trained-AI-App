import numpy as np
import random
import matplotlib.pyplot as plt

class QLearningInventory:
    def __init__(self, user_capacity, poisson_lambda, holding_cost, stockout_cost, 
                 gamma, alpha, epsilon, episodes, max_actions_per_episode):
        
        # Initialize parameters
        self.user_capacity = user_capacity
        self.poisson_lambda = poisson_lambda
        self.holding_cost = holding_cost
        self.stockout_cost = stockout_cost
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.episodes = episodes
        self.max_actions_per_episode = max_actions_per_episode
        self.batch = []  # Initialize the batch to store experiences

    def initialize_Q(self):
        # Initialize the Q-table as a dictionary
        Q = {}
        for alpha in range(self.user_capacity + 1):
            for beta in range(self.user_capacity + 1 - alpha):
                state = (alpha, beta)
                Q[state] = {}
                max_action = self.user_capacity - (alpha + beta)
                for action in range(max_action + 1):
                    Q[state][action] = np.random.uniform(0, 1)  # Small random values
        return Q

    def simulate_transition_and_reward(self, state, action):

        alpha, beta = state
        init_inv = alpha + beta
        demand = np.random.poisson(self.poisson_lambda)
        
        new_alpha = max(0, init_inv - demand)
        holding_cost = -new_alpha * self.holding_cost
        stockout_cost = 0
        
        if demand > init_inv:
            stockout_cost = -(demand - init_inv) * self.stockout_cost
        
        reward = holding_cost + stockout_cost
        next_state = (new_alpha, action)
        
        return next_state, reward

    def choose_action(self, state):

        # Epsilon-greedy action selection
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.user_capacity - (state[0] + state[1]) + 1)
        else:
            return max(self.Q[state], key=self.Q[state].get)

    def update_Q(self, batch):
        # Batch update of the Q-table
        for state, action, reward, next_state in batch:
            best_next_action = max(self.Q[next_state], key=self.Q[next_state].get)
            td_target = reward + self.gamma * self.Q[next_state][best_next_action]
            td_error = td_target - self.Q[state][action]
            self.Q[state][action] += self.alpha * td_error

    def train(self):

        self.Q = self.initialize_Q()  # Reinitialize Q-table for each training run

        for episode in range(self.episodes):
            alpha_0 = random.randint(0, self.user_capacity)
            beta_0 = random.randint(0, self.user_capacity - alpha_0)
            state = (alpha_0, beta_0)
            #total_reward = 0
            self.batch = []  # Reset the batch at the start of each episode
            action_taken = 0
            while action_taken < self.max_actions_per_episode:
                action = self.choose_action(state)
                next_state, reward = self.simulate_transition_and_reward(state, action)
                self.batch.append((state, action, reward, next_state))  # Collect experience
                state = next_state
                action_taken += 1
            
            self.update_Q(self.batch)  # Update Q-table using the batch
            

    def get_optimal_policy(self):
        optimal_policy = {}
        for state in self.Q.keys():
            optimal_policy[state] = max(self.Q[state], key=self.Q[state].get)
        return optimal_policy
    
    def test_policy(self, policy, episodes):
        """
        Test a given policy on the environment and calculate the total reward.

        Args:
            policy (dict): A dictionary mapping states to actions.
            episodes (int): The number of episodes to simulate.

        Returns:
            float: The total reward accumulated over all episodes.
        """
        total_reward = 0
        alpha_0 = random.randint(0, self.user_capacity)
        beta_0 = random.randint(0, self.user_capacity - alpha_0)
        state = (alpha_0, beta_0)  # Initialize the state
        
        for _ in range(episodes):

            action = policy.get(state, 0)
            next_state, reward = self.simulate_transition_and_reward(state, action)
            total_reward += reward
            state = next_state

        return total_reward
