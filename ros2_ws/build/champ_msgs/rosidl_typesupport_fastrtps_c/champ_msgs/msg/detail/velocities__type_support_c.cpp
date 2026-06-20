// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from champ_msgs:msg/Velocities.idl
// generated code does not contain a copyright notice
#include "champ_msgs/msg/detail/velocities__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "champ_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "champ_msgs/msg/detail/velocities__struct.h"
#include "champ_msgs/msg/detail/velocities__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _Velocities__ros_msg_type = champ_msgs__msg__Velocities;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
bool cdr_serialize_champ_msgs__msg__Velocities(
  const champ_msgs__msg__Velocities * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: linear_x
  {
    cdr << ros_message->linear_x;
  }

  // Field name: linear_y
  {
    cdr << ros_message->linear_y;
  }

  // Field name: angular_z
  {
    cdr << ros_message->angular_z;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
bool cdr_deserialize_champ_msgs__msg__Velocities(
  eprosima::fastcdr::Cdr & cdr,
  champ_msgs__msg__Velocities * ros_message)
{
  // Field name: linear_x
  {
    cdr >> ros_message->linear_x;
  }

  // Field name: linear_y
  {
    cdr >> ros_message->linear_y;
  }

  // Field name: angular_z
  {
    cdr >> ros_message->angular_z;
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t get_serialized_size_champ_msgs__msg__Velocities(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Velocities__ros_msg_type * ros_message = static_cast<const _Velocities__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: linear_x
  {
    size_t item_size = sizeof(ros_message->linear_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: linear_y
  {
    size_t item_size = sizeof(ros_message->linear_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: angular_z
  {
    size_t item_size = sizeof(ros_message->angular_z);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t max_serialized_size_champ_msgs__msg__Velocities(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: linear_x
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: linear_y
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: angular_z
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = champ_msgs__msg__Velocities;
    is_plain =
      (
      offsetof(DataType, angular_z) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
bool cdr_serialize_key_champ_msgs__msg__Velocities(
  const champ_msgs__msg__Velocities * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: linear_x
  {
    cdr << ros_message->linear_x;
  }

  // Field name: linear_y
  {
    cdr << ros_message->linear_y;
  }

  // Field name: angular_z
  {
    cdr << ros_message->angular_z;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t get_serialized_size_key_champ_msgs__msg__Velocities(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Velocities__ros_msg_type * ros_message = static_cast<const _Velocities__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: linear_x
  {
    size_t item_size = sizeof(ros_message->linear_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: linear_y
  {
    size_t item_size = sizeof(ros_message->linear_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: angular_z
  {
    size_t item_size = sizeof(ros_message->angular_z);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t max_serialized_size_key_champ_msgs__msg__Velocities(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: linear_x
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: linear_y
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: angular_z
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = champ_msgs__msg__Velocities;
    is_plain =
      (
      offsetof(DataType, angular_z) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _Velocities__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const champ_msgs__msg__Velocities * ros_message = static_cast<const champ_msgs__msg__Velocities *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_champ_msgs__msg__Velocities(ros_message, cdr);
}

static bool _Velocities__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  champ_msgs__msg__Velocities * ros_message = static_cast<champ_msgs__msg__Velocities *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_champ_msgs__msg__Velocities(cdr, ros_message);
}

static uint32_t _Velocities__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_champ_msgs__msg__Velocities(
      untyped_ros_message, 0));
}

static size_t _Velocities__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_champ_msgs__msg__Velocities(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Velocities = {
  "champ_msgs::msg",
  "Velocities",
  _Velocities__cdr_serialize,
  _Velocities__cdr_deserialize,
  _Velocities__get_serialized_size,
  _Velocities__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _Velocities__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Velocities,
  get_message_typesupport_handle_function,
  &champ_msgs__msg__Velocities__get_type_hash,
  &champ_msgs__msg__Velocities__get_type_description,
  &champ_msgs__msg__Velocities__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, champ_msgs, msg, Velocities)() {
  return &_Velocities__type_support;
}

#if defined(__cplusplus)
}
#endif
