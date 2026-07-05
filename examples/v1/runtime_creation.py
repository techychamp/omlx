from omlx.api.v1 import RuntimeBuilder

def main():
    print("Creating Runtime using fluent builder...")
    builder = RuntimeBuilder()
    runtime = (
        builder
        .configure({"log_level": "DEBUG"})
        .enable("SOME_NEW_FEATURE")
        .build()
    )
    print(f"Runtime state: {runtime.state}")
    print("Runtime created successfully.")

if __name__ == "__main__":
    main()
