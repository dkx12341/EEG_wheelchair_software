import time


def constantly_change_state():
    states = ["neutral", "left", "right", "push"]  # List of states
    current_state_index = 0  # Start with the first state
    message_count = 0  # Keep track of the number of messages

    while True:
        print(states[current_state_index])  # Print the current state
        message_count += 1  # Increment message count

        # Change state every 20 messages
        if message_count == 20:
            message_count = 0  # Reset message count
            current_state_index = (current_state_index + 1) % len(states)  # Move to the next state

        time.sleep(0.2)  # Wait for 0.2 seconds

# Start the function
constantly_change_state()