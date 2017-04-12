INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_KISS kiss)

FIND_PATH(
    KISS_INCLUDE_DIRS
    NAMES gr_kiss/api.h
    HINTS $ENV{KISS_DIR}/include
        ${PC_KISS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    KISS_LIBRARIES
    NAMES gnuradio-kiss
    HINTS $ENV{KISS_DIR}/lib
        ${PC_KISS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(KISS DEFAULT_MSG KISS_LIBRARIES KISS_INCLUDE_DIRS)
MARK_AS_ADVANCED(KISS_LIBRARIES KISS_INCLUDE_DIRS)

