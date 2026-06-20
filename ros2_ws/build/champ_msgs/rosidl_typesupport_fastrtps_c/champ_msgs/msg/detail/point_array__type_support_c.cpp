// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from champ_msgs:msg/PointArray.idl
// generated code does not contain a copyright notice
#include "champ_msgs/msg/detail/point_array__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "champ_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "champ_msgs/msg/detail/point_array__struct.h"
#include "champ_msgs/msg/detail/point_array__functions.h"
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

#include "champ_msgs/msg/detail/point__functions.h"  // lf, lh, rf, rh

// forward declare type support functions

bool cdr_serialize_champ_msgs__msg__Point(
  const champ_msgs__msg__Point * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_champ_msgs__msg__Point(
  eprosima::fastcdr::Cdr & cdr,
  champ_msgs__msg__Point * ros_message);

size_t get_serialized_size_champ_msgs__msg__Point(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_champ_msgs__msg__Point(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_champ_msgs__msg__Point(
  const champ_msgs__msg__Point * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_champ_msgs__msg__Point(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_champ_msgs__msg__Point(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, champ_msgs, msg, Point)();


using _PointArray__ros_msg_type = champ_msgs__msg__PointArray;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
bool cdr_serialize_champ_msgs__msg__PointArray(
  const champ_msgs__msg__PointArray * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: lf
  {
    cdr_serialize_champ_msgs__msg__Point(
      &ros_message->lf, cdr);
  }

  // Field name: rf
  {
    cdr_serialize_champ_msgs__msg__Point(
      &ros_message->rf, cdr);
  }

  // Field name: lh
  {
    cdr_serialize_champ_msgs__msg__Point(
      &ros_message->lh, cdr);
  }

  // Field name: rh
  {
    cdr_serialize_champ_msgs__msg__Point(
      &ros_message->rh, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
bool cdr_deserialize_champ_msgs__msg__PointArray(
  eprosima::fastcdr::Cdr & cdr,
  champ_msgs__msg__PointArray * ros_message)
{
  // Field name: lf
  {
    cdr_deserialize_champ_msgs__msg__Point(cdr, &ros_message->lf);
  }

  // Field name: rf
  {
    cdr_deserialize_champ_msgs__msg__Point(cdr, &ros_message->rf);
  }

  // Field name: lh
  {
    cdr_deserialize_champ_msgs__msg__Point(cdr, &ros_message->lh);
  }

  // Field name: rh
  {
    cdr_deserialize_champ_msgs__msg__Point(cdr, &ros_message->rh);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t get_serialized_size_champ_msgs__msg__PointArray(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _PointArray__ros_msg_type * ros_message = static_cast<const _PointArray__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: lf
  current_alignment += get_serialized_size_champ_msgs__msg__Point(
    &(ros_message->lf), current_alignment);

  // Field name: rf
  current_alignment += get_serialized_size_champ_msgs__msg__Point(
    &(ros_message->rf), current_alignment);

  // Field name: lh
  current_alignment += get_serialized_size_champ_msgs__msg__Point(
    &(ros_message->lh), current_alignment);

  // Field name: rh
  current_alignment += get_serialized_size_champ_msgs__msg__Point(
    &(ros_message->rh), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t max_serialized_size_champ_msgs__msg__PointArray(
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

  // Field name: lf
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: rf
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: lh
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: rh
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = champ_msgs__msg__PointArray;
    is_plain =
      (
      offsetof(DataType, rh) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
bool cdr_serialize_key_champ_msgs__msg__PointArray(
  const champ_msgs__msg__PointArray * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: lf
  {
    cdr_serialize_key_champ_msgs__msg__Point(
      &ros_message->lf, cdr);
  }

  // Field name: rf
  {
    cdr_serialize_key_champ_msgs__msg__Point(
      &ros_message->rf, cdr);
  }

  // Field name: lh
  {
    cdr_serialize_key_champ_msgs__msg__Point(
      &ros_message->lh, cdr);
  }

  // Field name: rh
  {
    cdr_serialize_key_champ_msgs__msg__Point(
      &ros_message->rh, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t get_serialized_size_key_champ_msgs__msg__PointArray(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _PointArray__ros_msg_type * ros_message = static_cast<const _PointArray__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: lf
  current_alignment += get_serialized_size_key_champ_msgs__msg__Point(
    &(ros_message->lf), current_alignment);

  // Field name: rf
  current_alignment += get_serialized_size_key_champ_msgs__msg__Point(
    &(ros_message->rf), current_alignment);

  // Field name: lh
  current_alignment += get_serialized_size_key_champ_msgs__msg__Point(
    &(ros_message->lh), current_alignment);

  // Field name: rh
  current_alignment += get_serialized_size_key_champ_msgs__msg__Point(
    &(ros_message->rh), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_champ_msgs
size_t max_serialized_size_key_champ_msgs__msg__PointArray(
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
  // Field name: lf
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: rf
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: lh
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: rh
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_champ_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = champ_msgs__msg__PointArray;
    is_plain =
      (
      offsetof(DataType, rh) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _PointArray__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const champ_msgs__msg__PointArray * ros_message = static_cast<const champ_msgs__msg__PointArray *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_champ_msgs__msg__PointArray(ros_message, cdr);
}

static bool _PointArray__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  champ_msgs__msg__PointArray * ros_message = static_cast<champ_msgs__msg__PointArray *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_champ_msgs__msg__PointArray(cdr, ros_message);
}

static uint32_t _PointArray__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_champ_msgs__msg__PointArray(
      untyped_ros_message, 0));
}

static size_t _PointArray__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_champ_msgs__msg__PointArray(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_PointArray = {
  "champ_msgs::msg",
  "PointArray",
  _PointArray__cdr_serialize,
  _PointArray__cdr_deserialize,
  _PointArray__get_serialized_size,
  _PointArray__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _PointArray__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_PointArray,
  get_message_typesupport_handle_function,
  &champ_msgs__msg__PointArray__get_type_hash,
  &champ_msgs__msg__PointArray__get_type_description,
  &champ_msgs__msg__PointArray__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, champ_msgs, msg, PointArray)() {
  return &_PointArray__type_support;
}

#if defined(__cplusplus)
}
#endif
