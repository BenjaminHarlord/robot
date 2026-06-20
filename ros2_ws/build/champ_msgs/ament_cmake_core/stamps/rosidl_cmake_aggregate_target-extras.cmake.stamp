# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target champ_msgs::champ_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${champ_msgs_TARGETS}.
if(champ_msgs_TARGETS AND NOT TARGET champ_msgs::champ_msgs)
  add_library(champ_msgs::champ_msgs INTERFACE IMPORTED)
  set_target_properties(champ_msgs::champ_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${champ_msgs_TARGETS}")
endif()
