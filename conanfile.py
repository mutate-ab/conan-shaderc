import os
import glob
from conans import ConanFile, CMake, tools


class ShadercConan(ConanFile):
    name = "shaderc"
    version = "2020.0"
    description = "A collection of tools, libraries, and tests for Vulkan shader compilation."
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    license = "Apache License 2.0"
    url = "https://github.com/mutate-ab/conan-shaderc"
    homepage = "https://github.com/google/shaderc"
    topics = ("conan", "opengl", "vulkan", "shaderc", "spirv")
    exports = "LICENSE"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    short_paths = True
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        sha256 = "e9ca32991e4544e8bbb0ff56403f3faa4775461af693999b213c22ecaf98615c"
        tools.get("https://codeload.github.com/google/shaderc/zip/v{}".format(self.version), sha256=sha256)
        extracted_folder = self.name + '-' + self.version
        os.rename(extracted_folder, self._source_subfolder)

        # Run shaderc's own git-sync-deps script to get dependencies
        import types
        import importlib.machinery
        sync_deps_path = os.path.join(os.path.abspath(self._source_subfolder), "utils/git-sync-deps")
        loader = importlib.machinery.SourceFileLoader('utils.git_sync_deps', sync_deps_path)
        mod = types.ModuleType(loader.name)
        mod.__file__ = sync_deps_path
        loader.exec_module(mod)
        mod.main([])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SHADERC_SKIP_TESTS"] = True
        cmake.definitions["SHADERC_ENABLE_WERROR_COMPILE"] = False
        cmake.definitions["EFFCEE_BUILD_TESTING"] = False
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

        if self.settings.os == "Macos" and self.options.shared:
            with tools.chdir(os.path.join(self._source_subfolder, 'src')):
                for filename in glob.glob('*.dylib'):
                    self.run('install_name_tool -id {filename} {filename}'.format(filename=filename))

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.pdb", dst="bin", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['m', 'dl', 'pthread'])
            if self.options.shared:
                self.cpp_info.exelinkflags.append("-lrt -lm -ldl")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Cocoa", "IOKit", "CoreVideo"])
