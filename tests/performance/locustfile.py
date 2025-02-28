from locust import HttpUser, task, between


class ProjectPerfTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def home(self):
        self.client.get("/")

    @task(3)
    def login(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task(3)
    def logout(self):
        self.client.get("/logout")

    @task(3)
    def points(self):
        self.client.get("/points")

    @task(3)
    def book(self):
        self.client.get("/book/Winter%20Coming")

    @task(3)
    def purchase(self):
        self.client.post(
            "/purchasePlaces", data={"competition": "Winter Coming", "places": 1}
        )
