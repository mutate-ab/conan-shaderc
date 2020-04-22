#include "spirv-tools/libspirv.h"
#include "shaderc/shaderc.h"

int main (void)
{
    spv_context ctx = spvContextCreate(SPV_ENV_VULKAN_1_1);
    spvContextDestroy(ctx);

    shaderc_compiler_t compiler = shaderc_compiler_initialize();
    shaderc_compiler_release(compiler);

    return 0;
}
