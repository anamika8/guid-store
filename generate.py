import secrets

class RandomGUIDGenerator:

    @staticmethod
    def generate():
        hex_string = '0123456789ABCDEF'
        generated_string = ''.join([secrets.choice(hex_string) for x in range(32)])
        return generated_string