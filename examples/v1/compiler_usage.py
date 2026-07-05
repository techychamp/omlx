import asyncio
from omlx.api.v1 import CompilerRequestBuilder

async def main():
    print("Building compiler request...")
    builder = CompilerRequestBuilder()
    request = (
        builder
        .with_model("my-custom-model-id")
        .with_backend("mlx")
        .enable_optimization("flash_attention")
        .build_request()
    )

    compiler = builder.build()
    print("Compiling synchronously...")
    result_sync = compiler.compile(request)
    print(f"Sync success: {result_sync.success}")

    print("Compiling asynchronously...")
    result_async = await compiler.compile_async(request)
    print(f"Async success: {result_async.success}")

if __name__ == "__main__":
    asyncio.run(main())
