import requests
import json

base = 'http://127.0.0.1:8001'

print('=== SIGNUP TEST ===')
try:
    r = requests.post(base + '/api/v1/auth/signup', 
                     json={'username': 'testuser2', 'email': 'test2@example.com', 'password': 'secret'}, 
                     timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text[:300]}')
except Exception as e:
    print(f'Error: {e}')

print('\n=== UPLOAD TEST ===')
try:
    with open('sample.jpg', 'rb') as f:
        r = requests.post(base + '/api/v1/photos/upload', 
                         files={'image': ('sample.jpg', f, 'image/jpeg')}, 
                         timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text[:300]}')
except Exception as e:
    print(f'Error: {e}')

print('\n=== ANALYZE TEST ===')
try:
    with open('sample.jpg', 'rb') as f:
        r = requests.post(base + '/api/v1/analyze/photo', 
                         files={'image': ('sample.jpg', f, 'image/jpeg')}, 
                         timeout=10)
    print(f'Status: {r.status_code}')
    
    if r.status_code in [200, 201]:
        data = r.json()
        required_fields = ['skin_type', 'hair_type', 'conditions_detected', 'confidence_scores']
        missing = [f for f in required_fields if f not in data]
        if missing:
            print(f'MISSING fields: {missing}')
        else:
            print('✓ All required fields present')
            print(f"  skin_type: {data['skin_type']}")
            print(f"  hair_type: {data['hair_type']}")
            print(f"  conditions_detected: {data['conditions_detected']}")
            print(f"  confidence_scores: {list(data['confidence_scores'].keys())}")
    else:
        print(f'Response: {r.text[:300]}')
except Exception as e:
    print(f'Error: {e}')
