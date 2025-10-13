import logfire

def setup_logging(service_name: str = "Financial-agent", env: str = "dev"):
    logfire.configure(
        service_name = service_name,
        environment = env,
        send_to_logfire = 'if-token-present'
    )

    logfire.install_auto_tracing(modules = ['httpx', 'yfinance', 'gradio'])