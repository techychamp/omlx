from omlx.api.v1 import BackendRequestBuilder, Inspector

def main():
    print("Selecting backend...")
    builder = BackendRequestBuilder()
    request = (
        builder
        .with_model_family("llama")
        .require_capability("attention")
        .build_request()
    )
    manager = builder.build()
    selection = manager.select_backend(request)
    print(f"Selected backend: {selection.selected_backend}")
    print(f"Reason: {selection.reason}")

    print("\nInspecting backend...")
    inspector = Inspector()
    inspection_result = inspector.inspect(selection.selected_backend)
    print(f"Health status: {inspection_result.health_status}")

if __name__ == "__main__":
    main()
