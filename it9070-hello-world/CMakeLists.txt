##
## Copyright 2020 - Joel Holdsworth <joel@airwebreathe.org.uk>
##

cmake_minimum_required(VERSION 3.0)

#
# Set up cross-build
#

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_COMPILER arm-none-eabi-gcc)

#
# Common options
#

set(CMAKE_C_FLAGS
  -Os
  -Werror
  -Wextra
  -ffreestanding
  -fno-asynchronous-unwind-tables
  -fno-exceptions
  -mcpu=fa626
  --specs=nosys.specs)
string(REPLACE ";" " " CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")

set(CMAKE_EXE_LINKER_FLAGS
  -nostartfiles
  -Wl,-T${CMAKE_SOURCE_DIR}/src/default.lds)
string(REPLACE ";" " " CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS}")

#
# Set up project
#

project(i9070_hello_world VERSION 0.1.0 LANGUAGES C)

#
# Sources
#

add_executable(
  ${PROJECT_NAME}
  src/startup.S
  src/main.c
)
