# Optional: For local testing before deploying to Lambda
if __name__ == '__main__':
    test_event = {
        'httpMethod': 'POST',  # Example method
        'path': '/guid'  # Example path
    }
    print(lambda_handler(test_event, None))

