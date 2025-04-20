import requests

response = requests.post("http://localhost:8001/nowpayments/ipn", json={
    "payment_id": "5078465634",  # ✅ правильно!
    "payment_status": "finished"
})

print("✅ Status:", response.status_code)
print("🔁 Response:", response.json())
