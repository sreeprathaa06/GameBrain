from collections import deque
import random


class ReplayBuffer:
    """
    Stores experiences for DQN training.

    Each experience is:
    (state, action, reward, next_state, done)
    """

    def __init__(self, capacity=10000):
        """
        Create an empty replay buffer.

        Args:
            capacity: Maximum number of experiences to store.
        """
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """
        Add one experience to the buffer.
        """
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)

    def sample(self, batch_size):
        """
        Randomly sample a batch of experiences.
        """
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        """
        Return the current number of stored experiences.
        """
        return len(self.buffer)

if __name__ == "__main__":

    buffer = ReplayBuffer(capacity=5)

    for i in range(5):
        buffer.push(
            state=i,
            action=i % 4,
            reward=1,
            next_state=i + 1,
            done=False
        )

    print("Buffer Size:", len(buffer))

    print("\nRandom Sample:")

    samples = buffer.sample(2)

    for sample in samples:
        print(sample)