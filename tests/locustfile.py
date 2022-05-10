from locust import task, FastHttpUser

class LoadTest(FastHttpUser):
    @task
    def scan(self):
        create = self.client.post("/repository", json={"url": "https://github.com/dyne/restroom-template"})
        scan = self.client.post("/scan", json={"url": "https://github.com/dyne/restroom-template"})
