from conans import ConanFile, CMake, tools
import os


class DatastaxcppdriverConan(ConanFile):
    name = "datastax-cpp-driver"
    version = "2.8.1"
    license = "Apache 2.0"
    url = "https://github.com/kmaragon/conan-datastax-cpp-driver"
    description = "Conan package for Datastax Open Source C++ driver (non-DSE)"
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "multicore_compilation": [True, False],
            "use_boost_atomic": [True, False],
            "use_cpp_atomic": [True, False],
            "use_openssl": [True, False],
            "use_tcmalloc": [True, False],
            "use_zlib": [True, False]
        }
    requires = "libuv/1.15.0@bincrafters/stable"
    default_options = "shared=False", "multicore_compilation=True", "use_boost_atomic=False", "use_cpp_atomic=True", "use_openssl=True", "use_tcmalloc=False", "use_zlib=True"
    generators = "cmake"

    def configure(self):
        if self.options.use_boost_atomic:
            if self.options.use_cpp_atomic:
                raise ConanException("Only one of use_boost_atomic and use_cpp_atomic should be used")
            self.requires("Boost/1.66.0@conan/stable")

        if self.options.use_openssl:
            self.requires("OpenSSL/1.0.2o@conan/stable")

        if self.options.use_zlib:
            self.requires("zlib/1.2.11@conan/stable")


    def source(self):
        tools.download("https://github.com/datastax/cpp-driver/archive/{}.tar.gz".format(self.version), "datastax-cpp-driver.tar.gz")
        tools.unzip("datastax-cpp-driver.tar.gz")
        os.unlink("datastax-cpp-driver.tar.gz")
        
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("cpp-driver-{}/CMakeLists.txt".format(self.version), "include(CppDriver)",
                              '''include(CppDriver)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)

        cmake.definitions["CASS_BUILD_DOCS"] = "OFF"
        cmake.definitions["CASS_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["CASS_BUILD_INTEGRATION_TESTS"] = "OFF"
        cmake.definitions["CASS_BUILD_SHARED"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["CASS_BUILD_STATIC"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["CASS_BUILD_TESTS"] = "OFF"
        cmake.definitions["CASS_BUILD_UNIT_TESTS"] = "OFF"
        cmake.definitions["CASS_DEBUG_CUSTOM_ALLOC"] = "OFF"
        cmake.definitions["CASS_INSTALL_HEADER"] = "ON"
        cmake.definitions["CASS_INSTALL_PKG_CONFIG"] = "OFF"
        cmake.definitions["CASS_MULTICORE_COMPILATION"] = "ON" if self.options.multicore_compilation else "OFF"
        cmake.definitions["CASS_USE_BOOST_ATOMIC"] = "ON" if self.options.use_boost_atomic else "OFF"
        cmake.definitions["CASS_USE_STD_ATOMIC"] = "ON" if self.options.use_cpp_atomic else "OFF"
        cmake.definitions["CASS_USE_LIBSSH2"] = "OFF"
        cmake.definitions["CASS_USE_OPENSSL"] = "ON" if self.options.use_openssl else "OFF"
        cmake.definitions["CASS_USE_TCMALLOC"] = "ON" if self.options.use_tcmalloc else "OFF"
        cmake.definitions["CASS_USE_STATIC_LIBS"] = "ON"
        cmake.definitions["CASS_USE_ZLIB"] = "ON" if self.options.use_zlib else "OFF"

        cmake.configure(source_folder="cpp-driver-{}".format(self.version))
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        cmake = CMake(self)
        cmake.configure(source_folder="cpp-driver-{}".format(self.version))
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        if self.options.shared:
            self.cpp_info.libs = ["cassandra"]
        else:
            self.cpp_info.libs = ["cassandra_static"]
        self.cpp_info.bindirs = ["bin"]

