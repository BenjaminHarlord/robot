// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/PID.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/pid__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__PID__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x25, 0xf5, 0x19, 0x8c, 0x1c, 0x9d, 0x7f, 0xd5,
      0x45, 0xbe, 0x75, 0x0e, 0x16, 0x0a, 0x37, 0xf1,
      0x12, 0xf3, 0xe2, 0x04, 0x02, 0x30, 0xdd, 0x2f,
      0x60, 0xfd, 0xbb, 0x50, 0x60, 0x3b, 0xa4, 0x49,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char champ_msgs__msg__PID__TYPE_NAME[] = "champ_msgs/msg/PID";

// Define type names, field names, and default values
static char champ_msgs__msg__PID__FIELD_NAME__p[] = "p";
static char champ_msgs__msg__PID__FIELD_NAME__d[] = "d";
static char champ_msgs__msg__PID__FIELD_NAME__i[] = "i";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__PID__FIELDS[] = {
  {
    {champ_msgs__msg__PID__FIELD_NAME__p, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__PID__FIELD_NAME__d, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__PID__FIELD_NAME__i, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
champ_msgs__msg__PID__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__PID__TYPE_NAME, 18, 18},
      {champ_msgs__msg__PID__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32 p\n"
  "float32 d\n"
  "float32 i";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__PID__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__PID__TYPE_NAME, 18, 18},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 30, 30},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__PID__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__PID__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
