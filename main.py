from fastapi import FastAPI
from pydevlens.tracing import Tracer
from pydevlens.profiling import profile_code

app = FastAPI()

tracer = Tracer()

@app.get("/")
def read_root():
    tracer.start_trace()
    response = {"message": "Welcome to PyDevLens!"}
    tracer.stop_trace()
    return response

@app.get("/profile")
@profile_code
def profile_example():
    # Dummy function to simulate workload
    total = 0
    for i in range(100000):
        total += i
    return {"result": total}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pydevlens.main:app", host="127.0.0.1", port=8000, reload=True)
