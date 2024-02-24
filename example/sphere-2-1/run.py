import docker

client = docker.from_env()

container = client.containers.run("mysphere:latest",
                                  environment={},
                                  stdin_open=True,
                                  detach=True)
print("aa")
socket = container.attach_socket(
    params={"stdin": 1, "stream": 1, "stdout": 1, "stderr": 1}
)
print("ii")
socket._sock.sendall(
    "[1,2]\n".encode("utf-8")
)
print("uu")
container.wait(timeout=10)
stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
print(stdout)