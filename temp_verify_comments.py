from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
create_task = client.post('/tasks', json={'title': 'Demo'})
task_id = create_task.json()['id']
add_comment = client.post(f'/tasks/{task_id}/comments', json={'text': 'hello'})
print(create_task.status_code)
print(add_comment.status_code)
print(add_comment.json()['text'])
print(client.get(f'/tasks/{task_id}/comments').status_code)
print(client.delete(f"/tasks/{task_id}/comments/{add_comment.json()['id']}").status_code)
print(client.get(f'/tasks/{task_id}/comments').json())
