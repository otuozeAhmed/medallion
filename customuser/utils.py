import random

def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join(random.choice('0123456789') for _ in range(6))
