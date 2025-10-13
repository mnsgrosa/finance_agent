import httpx


def get_ticker(company_name: str) -> str:
    company_name = company_name.lower()
    with httpx.Client() as client:
        response = client.post("http://localhost:8000/get_ticker", json = {"company_name": company_name})
        if response.status_code == 200:
            return response.json().get("ticker", "")
    return ""