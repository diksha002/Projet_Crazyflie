cmake_minimum_required(VERSION 3.8)
project(crazyflie_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install launch files
install(DIRECTORY
  launch
  urdf
  meshes
  rviz
  config
  DESTINATION share/${PROJECT_NAME}/
)

# Install entire scripts directory (if all .py files are executables)
 install(DIRECTORY
   scripts
   DESTINATION lib/${PROJECT_NAME}
   USE_SOURCE_PERMISSIONS
   PATTERN "*.py" PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ
 )



ament_package()
