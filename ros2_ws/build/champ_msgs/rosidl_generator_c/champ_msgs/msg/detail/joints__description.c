// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/Joints.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/joints__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__Joints__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x0e, 0x64, 0x48, 0x43, 0x69, 0xd6, 0x98, 0xd0,
      0x8b, 0x78, 0x20, 0x47, 0xb3, 0x94, 0x7a, 0x6d,
      0xce, 0xda, 0xfd, 0x54, 0x8f, 0x94, 0xa0, 0xa3,
      0x19, 0xa5, 0x1f, 0xbe, 0xe7, 0x7c, 0xae, 0x86,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char champ_msgs__msg__Joints__TYPE_NAME[] = "champ_msgs/msg/Joints";

// Define type names, field names, and default values
static char champ_msgs__msg__Joints__FIELD_NAME__position[] = "position";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__Joints__FIELDS[] = {
  {
    {champ_msgs__msg__Joints__FIELD_NAME__position, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
champ_msgs__msg__Joints__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__Joints__TYPE_NAME, 21, 21},
      {champ_msgs__msg__Joints__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32[] position";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__Joints__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__Joints__TYPE_NAME, 21, 21},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 18, 18},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__Joints__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__Joints__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
