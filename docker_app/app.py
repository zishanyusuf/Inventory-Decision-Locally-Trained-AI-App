import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.auth import Auth
from config_file import Config
from models.order_model import QLearningInventory


########################################################
#Commented out the code responsible for Authentication
# # ID of Secrets Manager containing cognito parameters
# secrets_manager_id = Config.SECRETS_MANAGER_ID

# # ID of the AWS region in which Secrets Manager is deployed
# region = Config.DEPLOYMENT_REGION

# # Initialise CognitoAuthenticator
# authenticator = Auth.get_authenticator(secrets_manager_id, region)

# # Authenticate user, and stop here if not logged in
# is_logged_in = authenticator.login()
# if not is_logged_in:
#     st.stop()


# def logout():
#     authenticator.logout()
 

# with st.sidebar:
#     st.text(f"Welcome,\n{authenticator.get_username()}")
#     st.button("Logout", "logout_btn", on_click=logout)


def main():
    # Title and description
    st.title("📊 Inventory Decision AI App and Visualization")
    st.markdown("""
    This application demonstrates inventory management optimization using Q-Learning.
    Adjust the parameters in the sidebar to see how they affect the optimal policy.
    """)

    # Add social links in sidebar
    with st.sidebar:
        # st.markdown("### Zishan Yusuf")
        st.markdown("<p style='font-size: 20px; font-weight: bold; margin-top: 0.25px; margin-bottom: 1px;'>Zishan Yusuf</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 15px; font-weight:; margin-bottom: 4px;'>Supply Chain and Technology Enthusiast</p>", unsafe_allow_html=True)
        cols = st.columns(7)
        with cols[0]:
            st.markdown("""
                <a href="https://www.linkedin.com/in/zishan-yusuf/" target="_blank">
                    <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" alt="" width="30" height="30"/>
                </a>
                """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown("""
                <a href="https://github.com/zishanyusuf?tab=repositories" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" width="30" height="30"/>
                </a>
                """, unsafe_allow_html=True)
        st.markdown("---")  # Adds a horizontal line for separation
        st.markdown("Inspired by **Peyman Kor** BlogPost on Reinforcement Learning")
        cols = st.columns(7)
        with cols[0]:
            st.markdown("""
                <a href="https://medium.com/towards-data-science/optimizing-inventory-management-with-reinforcement-learning-a-hands-on-python-guide-7833df3d25a6" target="_blank">
                    <img src="https://cdn0.iconfinder.com/data/icons/picons-social/57/108-medium-1024.png" alt="" width="30" height="30"/>
                </a>
                """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown("""
                <a href="https://www.linkedin.com/in/peyman-kor/" target="_blank">
                    <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" alt="" width="30" height="30"/>
                </a>
                """, unsafe_allow_html=True)
        st.markdown("---")  # Adds a horizontal line for separation    
    # Sidebar parameters
    st.sidebar.header("Model Parameters")
    
    user_capacity = st.sidebar.slider("Storage Capacity", 5, 20, 10)
    poisson_lambda = st.sidebar.slider("Demand Rate (λ)", 1, 10, 4)
    holding_cost = st.sidebar.slider("Holding Cost", 1, 20, 8)
    stockout_cost = st.sidebar.slider("Stockout Cost", 1, 20, 10)
    
    # Advanced parameters with expander
    with st.sidebar.expander("Advanced Parameters"):
        gamma = st.slider("Discount Factor (γ)", 0.1, 1.0, 0.9)
        alpha = st.slider("Learning Rate (α)", 0.01, 1.0, 0.1)
        epsilon = st.slider("Exploration Rate (ε)", 0.01, 1.0, 0.1)
        episodes = st.slider("Training Episodes", 100, 5000, 1000)
        max_actions = st.slider("Max Actions per Episode", 100, 2000, 1000)

    # Initialize and train model
    try:
        with st.spinner('Training Local Reinforcement-Learning model in progress...'):
            ql = QLearningInventory(
                user_capacity=user_capacity,
                poisson_lambda=poisson_lambda,
                holding_cost=holding_cost,
                stockout_cost=stockout_cost,
                gamma=gamma,
                alpha=alpha,
                epsilon=epsilon,
                episodes=episodes,
                max_actions_per_episode=max_actions
            )
            ql.train()
            optimal_policy = ql.get_optimal_policy()
            st.success('AI training completed! - Local Reinforcement Learning model.')

        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Q-Learning Policy", "Policy Comparison", "Performance Metrics"])

        with tab1:
            st.header("Q-Learning Policy Visualization")
            
            # Visualization of optimal policy
            states = list(optimal_policy.keys())
            n_states = len(states)
            x = np.arange(n_states)

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(x, [optimal_policy[state] for state in states],
                  color='purple', alpha=0.6)
            ax.set_xlabel('State (Inventory Level)')
            ax.set_ylabel('Order Quantity')
            ax.set_title('Optimal Order Quantities by State')
            st.pyplot(fig)

            # Show raw data in expander
            with st.expander("Show Raw Policy Data"):
                st.dataframe({
                    'State': states,
                    'Order Quantity': [optimal_policy[state] for state in states]
                })

        with tab2:
            st.header("Policy Comparison")
            
            # Simple policy for comparison
            def order_up_to_policy(state, capacity, target_level):
                alpha, beta = state
                max_possible_order = capacity - (alpha + beta)
                desired_order = max(0, target_level - (alpha + beta))
                return min(max_possible_order, desired_order)

            target_level = st.slider("Target Level for Simple Policy", 0, user_capacity, user_capacity//2)
            simple_policy = {state: order_up_to_policy(state, user_capacity, target_level) 
                           for state in optimal_policy.keys()}

            # Create comparison plot
            fig, ax = plt.subplots(figsize=(12, 6))
            bar_width = 0.35
            ax.bar(x - bar_width/2, [optimal_policy[state] for state in states],
                  bar_width, label='Q-Learning Policy', color='purple', alpha=0.6)
            ax.bar(x + bar_width/2, [simple_policy[state] for state in states],
                  bar_width, label='Simple Policy', color='orange', alpha=0.6)
            ax.set_xlabel('State')
            ax.set_ylabel('Order Quantity')
            ax.legend()
            st.pyplot(fig)

        with tab3:
            st.header("Performance Metrics")
            
            # Calculate and display performance metrics
            col1, col2 = st.columns(2)
            
            with col1:
                episodes_val = 1000
                q_reward = ql.test_policy(optimal_policy, episodes_val)
                simple_reward = ql.test_policy(simple_policy, episodes_val)
                
                st.metric(
                    label="Q-Learning Policy Total Cost",
                    value=f"{-q_reward:.2f}",
                    delta=f"{(simple_reward - q_reward):.2f}"
                )
                
            with col2:
                st.metric(
                    label="Simple Policy Total Cost",
                    value=f"{-simple_reward:.2f}",
                    delta=f"{(q_reward - simple_reward):.2f}"
                )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please adjust the parameters and try again.")

    # Add download functionality
    if st.button("Download Results"):
        results_df = pd.DataFrame({
            'State': states,
            'Q_Learning_Policy': [optimal_policy[state] for state in states],
            'Simple_Policy': [simple_policy[state] for state in states]
        })
        st.download_button(
            label="Download CSV",
            data=results_df.to_csv(index=False),
            file_name="inventory_policy_results.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    # Page configuration
    main()